"""SQLite 持久化：连接与建表（Docker 内 /data/stock.db）。"""
from __future__ import annotations

import datetime as _dt
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("STOCK_DB_PATH", "/data/stock.db"))
IMAGES_DIR = Path(os.environ.get("STOCK_IMAGES_DIR", "/data/images"))


def _ensure_parent() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_conn() -> sqlite3.Connection:
    _ensure_parent()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    _ensure_parent()
    conn = get_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                sort_order  INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name        TEXT NOT NULL,
                quantity    REAL NOT NULL DEFAULT 0,
                unit        TEXT NOT NULL DEFAULT '个',
                threshold   REAL NOT NULL DEFAULT 0,
                expiry_date TEXT,
                note        TEXT,
                archived    INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
                    ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);
            CREATE INDEX IF NOT EXISTS idx_items_archived ON items(archived);
            """
        )
        # 轻量迁移：老库补 image 列
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(items)").fetchall()}
        if "image" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN image TEXT")
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def today_str() -> str:
    return _dt.date.today().isoformat()
