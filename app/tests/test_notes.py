from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_and_list_note():
    resp = client.post("/notes", json={"title": "Test note", "body": "hello"})
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "Test note"
    assert "id" in created

    resp = client.get("/notes")
    assert resp.status_code == 200
    titles = [n["title"] for n in resp.json()]
    assert "Test note" in titles