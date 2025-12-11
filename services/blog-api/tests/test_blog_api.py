def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_list_posts(client):
    res = client.get("/posts")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    titles = [p["title"] for p in data]
    assert "First Post" in titles
    assert "Second Post" in titles


def test_get_post(client):
    res = client.get("/posts/1")
    assert res.status_code == 200
    body = res.get_json()
    assert body["title"] == "First Post"
    assert body["content"] == "First content"


def test_create_post(client):
    res = client.post("/posts", json={"title": "New", "content": "Body"})
    assert res.status_code == 201
    created = res.get_json()
    assert created["title"] == "New"

    # now list to confirm
    res2 = client.get("/posts")
    assert any(p["title"] == "New" for p in res2.get_json())


def test_update_post(client):
    res = client.put("/posts/1", json={"title": "Edited", "content": "Edited body"})
    assert res.status_code == 200
    assert res.get_json()["title"] == "Edited"


def test_delete_post(client):
    res = client.delete("/posts/1")
    assert res.status_code == 200
    assert "deleted" in res.get_json()["message"].lower()

    res2 = client.get("/posts/1")
    assert res2.status_code == 404


def test_validation(client):
    res = client.post("/posts", json={"title": "", "content": "x"})
    assert res.status_code == 400
    res = client.put("/posts/1", json={"title": "ok", "content": ""})
    assert res.status_code == 400
