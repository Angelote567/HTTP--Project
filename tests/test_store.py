from usj_http.store import CatStore


def test_basic_crud():
    store = CatStore()
    created = store.create({"name": "Milo", "breed": "Tabby", "age": 2})
    assert created["id"] >= 3
    fetched = store.get(created["id"])
    assert fetched["name"] == "Milo"
    updated = store.update(created["id"], {"name": "Milo", "breed": "Tabby", "age": 3})
    assert updated["age"] == 3
    assert store.delete(created["id"]) is True
    assert store.get(created["id"]) is None
