import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.app import app


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == "Flask DevOps assessment application is running"