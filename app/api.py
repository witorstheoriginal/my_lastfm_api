from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from .models import Item, ItemCreate
from .store import InMemoryStore

app = FastAPI(title="My HTTP API")

store = InMemoryStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items", response_model=list[Item])
def list_items() -> list[Item]:
    return store.list_items()


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    item = store.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    return store.create_item(payload)


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    ok = store.delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
