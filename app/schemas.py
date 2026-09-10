"""Pydantic 请求/响应模型。"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    sort_order: int = 0


class CategoryOut(CategoryIn):
    id: int


class ItemIn(BaseModel):
    category_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=128)
    quantity: float = 0
    unit: str = Field(default="个", max_length=16)
    threshold: float = 0
    expiry_date: Optional[str] = None  # YYYY-MM-DD
    note: Optional[str] = None
    archived: bool = False


class ItemOut(BaseModel):
    id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    name: str
    quantity: float
    unit: str
    threshold: float
    expiry_date: Optional[str] = None
    note: Optional[str] = None
    archived: bool
    image: Optional[str] = None
    low_stock: bool
    expired: bool
    expiring_soon: bool
    created_at: str
    updated_at: str


class QuantityDelta(BaseModel):
    delta: float = Field(..., description="增量，可为正/负")
