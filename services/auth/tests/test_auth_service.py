def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_signup_and_login_flow(client):
    # signup new user
    res = client.post("/signup", json={"username": "bob", "password": "pw12345"})
    assert res.status_code == 201
    body = res.get_json()
    assert "token" in body
    assert body["user"]["username"] == "bob"

    # login existing user
    res2 = client.post("/login", json={"username": "bob", "password": "pw12345"})
    assert res2.status_code == 200
    assert "token" in res2.get_json()


def test_login_invalid(client):
    res = client.post("/login", json={"username": "alice", "password": "bad"})
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/me")
    assert res.status_code == 401


def test_me_with_token(client):
    res = client.post("/login", json={"username": "alice", "password": "password123"})
    token = res.get_json()["token"]
    res2 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    assert res2.get_json()["username"] == "alice"


def test_signup_duplicate_username(client):
    res = client.post("/signup", json={"username": "alice", "password": "another"})
    assert res.status_code == 409
