from __future__ import annotations

from datetime import datetime, timezone

from .models import Item, ItemCreate


class InMemoryStore:
    def __init__(self) -> None:
        self._items: dict[int, Item] = {}
        self._next_id: int = 1

    def list_items(self) -> list[Item]:
        return list(self._items.values())

    def get_item(self, item_id: int) -> Item | None:
        return self._items.get(item_id)

    def create_item(self, payload: ItemCreate) -> Item:
        item = Item(
            id=self._next_id,
            name=payload.name,
            price=payload.price,
            tags=payload.tags,
            created_at=datetime.now(timezone.utc),
        )
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def delete_item(self, item_id: int) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
