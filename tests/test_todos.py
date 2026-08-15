async def test_create_and_list(client):
    r = await client.post("/todos", json={"title": "write tests"})
    assert r.status_code == 201
    created = r.json()
    assert created["title"] == "write tests"
    assert not created["done"]

    r = await client.get("/todos")
    assert [t["id"] for t in r.json()] == [created["id"]]


async def test_isolation(client):
    """check previous test was rolled back by session manager"""
    r = await client.get("/todos")
    assert r.json() == []


async def test_patch_partial(client):
    r = await client.post("/todos", json={"title": "original"})
    todo_id = r.json()["id"]

    r = await client.patch(f"/todos/{todo_id}", json={"done": "true"})
    assert r.json()["title"] == "original"
    assert r.json()["done"]


async def test_validation_rejects_empty_title(client):
    r = await client.post("/todos", json={"title": ""})
    assert r.status_code == 422


async def test_404(client):
    r = await client.patch("/todos/4321", json={"done": "true"})
    assert r.status_code == 404
