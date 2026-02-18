from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_crud_flow() -> None:
    r = client.post("/items", json={"name": "Penna", "price": 1.5, "tags": ["stationery"]})
    assert r.status_code == 201
    created = r.json()
    assert created["id"] >= 1
    assert created["name"] == "Penna"

    item_id = created["id"]

    r = client.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id

    r = client.get("/items")
    assert r.status_code == 200
    assert any(x["id"] == item_id for x in r.json())

    r = client.delete(f"/items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/items/{item_id}")
    assert r.status_code == 404


def test_validation() -> None:
    r = client.post("/items", json={"name": "", "price": -1})
    assert r.status_code == 422
