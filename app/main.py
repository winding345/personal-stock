"""FastAPI 入口：REST API + 移动端 SPA 静态托管。"""
from __future__ import annotations

import datetime as _dt
import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from .db import get_conn, init_db, now_iso, today_str
from .schemas import CategoryIn, CategoryOut, ItemIn, ItemOut, QuantityDelta

app = FastAPI(title="Personal Stock", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"


@app.on_event("startup")
def _startup() -> None:
    init_db()


# ---------------- helpers ----------------

def _compute_flags(quantity: float, threshold: float, expiry_date: str | None) -> dict:
    low_stock = bool(threshold >= 0 and quantity <= threshold) if threshold else bool(quantity <= 0)
    expired = False
    expiring_soon = False
    if expiry_date:
        try:
            d = _dt.date.fromisoformat(expiry_date)
            delta_days = (d - _dt.date.today()).days
            expired = delta_days < 0
            expiring_soon = 0 <= delta_days <= 30
        except ValueError:
            pass
    return {"low_stock": low_stock, "expired": expired, "expiring_soon": expiring_soon}


def _row_item_to_out(row: sqlite3.Row) -> ItemOut:
    d = dict(row)
    flags = _compute_flags(d["quantity"], d["threshold"], d["expiry_date"])
    return ItemOut(
        id=d["id"],
        category_id=d["category_id"],
        category_name=d["category_name"],
        name=d["name"],
        quantity=d["quantity"],
        unit=d["unit"],
        threshold=d["threshold"],
        expiry_date=d["expiry_date"],
        note=d["note"],
        archived=bool(d["archived"]),
        low_stock=flags["low_stock"],
        expired=flags["expired"],
        expiring_soon=flags["expiring_soon"],
        created_at=d["created_at"],
        updated_at=d["updated_at"],
    )


_ITEM_SELECT = """
    SELECT i.*, c.name AS category_name
    FROM items i
    LEFT JOIN categories c ON c.id = i.category_id
"""


# ---------------- items ----------------

@app.get("/api/items", response_model=list[ItemOut])
def list_items(
    category_id: int | None = None,
    include_archived: bool = False,
    flag: str | None = Query(None, description="low_stock|expired|expiring_soon"),
):
    sql = _ITEM_SELECT + " WHERE 1=1"
    params: list = []
    if category_id is not None:
        sql += " AND i.category_id = ?"
        params.append(category_id)
    if not include_archived:
        sql += " AND i.archived = 0"
    sql += " ORDER BY c.sort_order ASC, c.name ASC, i.name ASC"
    conn = get_conn()
    try:
        rows = conn.execute(sql, params).fetchall()
        # apply post-filter on computed flags (server-side flags)
        if flag:
            out = []
            for r in rows:
                o = _row_item_to_out(r)
                f = getattr(o, flag)
                if f:
                    out.append(o)
            return out
        return [_row_item_to_out(r) for r in rows]
    finally:
        conn.close()


def _get_item_or_404(conn: sqlite3.Connection, item_id: int) -> sqlite3.Row:
    row = conn.execute(
        _ITEM_SELECT + " WHERE i.id = ?", (item_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="物品不存在")
    return row


@app.post("/api/items", response_model=ItemOut)
def create_item(item: ItemIn):
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO items
                (category_id, name, quantity, unit, threshold, expiry_date, note, archived, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                item.category_id,
                item.name.strip(),
                item.quantity,
                item.unit or "个",
                item.threshold,
                item.expiry_date,
                item.note,
                1 if item.archived else 0,
                now_iso(),
                now_iso(),
            ),
        )
        conn.commit()
        row = conn.execute(_ITEM_SELECT + " WHERE i.id = ?", (cur.lastrowid,)).fetchone()
        return _row_item_to_out(row)
    finally:
        conn.close()


@app.put("/api/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, item: ItemIn):
    conn = get_conn()
    try:
        _get_item_or_404(conn, item_id)
        now = now_iso()
        conn.execute(
            """
            UPDATE items SET
                category_id=?, name=?, quantity=?, unit=?, threshold=?,
                expiry_date=?, note=?, archived=?, updated_at=?
            WHERE id=?
            """,
            (
                item.category_id,
                item.name.strip(),
                item.quantity,
                item.unit or "个",
                item.threshold,
                item.expiry_date,
                item.note,
                1 if item.archived else 0,
                now,
                item_id,
            ),
        )
        conn.commit()
        row = conn.execute(_ITEM_SELECT + " WHERE i.id = ?", (item_id,)).fetchone()
        return _row_item_to_out(row)
    finally:
        conn.close()


@app.post("/api/items/{item_id}/quantity", response_model=ItemOut)
def adjust_quantity(item_id: int, body: QuantityDelta):
    """快速 +1/-1 等数量调整。"""
    conn = get_conn()
    try:
        row = _get_item_or_404(conn, item_id)
        new_qty = float(row["quantity"]) + body.delta
        if new_qty < 0:
            new_qty = 0.0
        conn.execute(
            "UPDATE items SET quantity=?, updated_at=? WHERE id=?",
            (new_qty, now_iso(), item_id),
        )
        conn.commit()
        row = conn.execute(_ITEM_SELECT + " WHERE i.id = ?", (item_id,)).fetchone()
        return _row_item_to_out(row)
    finally:
        conn.close()


@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM items WHERE id=?", (item_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="物品不存在")
        return {"ok": True}
    finally:
        conn.close()


# ---------------- categories ----------------

@app.get("/api/categories", response_model=list[CategoryOut])
def list_categories():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM categories ORDER BY sort_order ASC, id ASC"
        ).fetchall()
        return [CategoryOut(**dict(r)) for r in rows]
    finally:
        conn.close()


@app.post("/api/categories", response_model=CategoryOut)
def create_category(body: CategoryIn):
    conn = get_conn()
    try:
        now = now_iso()
        try:
            cur = conn.execute(
                "INSERT INTO categories (name, sort_order, created_at, updated_at) VALUES (?,?,?,?)",
                (body.name.strip(), body.sort_order, now, now),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="分类已存在")
        row = conn.execute("SELECT * FROM categories WHERE id=?", (cur.lastrowid,)).fetchone()
        return CategoryOut(**dict(row))
    finally:
        conn.close()


@app.delete("/api/categories/{cat_id}")
def delete_category(cat_id: int):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


# ---------------- misc ----------------

@app.get("/api/export")
def export_json():
    """导出全量数据为 JSON，便于备份/迁移。"""
    conn = get_conn()
    try:
        cats = [dict(r) for r in conn.execute("SELECT * FROM categories").fetchall()]
        items = [dict(r) for r in conn.execute("SELECT * FROM items").fetchall()]
        payload = {"exported_at": now_iso(), "categories": cats, "items": items}
        return Response(
            content=json.dumps(payload, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="stock_backup.json"'},
        )
    finally:
        conn.close()


@app.get("/api/stats")
def stats():
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS total, SUM(CASE WHEN archived=0 THEN 1 ELSE 0 END) AS active "
            "FROM items"
        ).fetchone()
        active = row["active"] or 0
        flag_rows = conn.execute("SELECT * FROM items WHERE archived=0").fetchall()
        low = sum(1 for r in flag_rows if _compute_flags(r["quantity"], r["threshold"], r["expiry_date"])["low_stock"])
        expired = sum(1 for r in flag_rows if _compute_flags(r["quantity"], r["threshold"], r["expiry_date"])["expired"])
        near = sum(1 for r in flag_rows if _compute_flags(r["quantity"], r["threshold"], r["expiry_date"])["expiring_soon"])
        return {"total": row["total"], "active": active, "low_stock": low, "expired": expired, "expiring_soon": near}
    finally:
        conn.close()


# ---------------- SPA ----------------

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")
