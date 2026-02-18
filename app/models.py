from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    tags: list[str] = Field(default_factory=list)


class Item(ItemCreate):
    id: int
    created_at: datetime
