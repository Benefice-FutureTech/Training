from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"Hello": "World"}

def test_create_user():
    user_data = {"username": "testuser", "password": "12345"}
    resp = client.post("/users/", json=user_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_get_users():
    resp = client.get("/users/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
