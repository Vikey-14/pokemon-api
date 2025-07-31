# tests/download/test_download.py

import os
import io
from pathlib import Path
from fastapi.testclient import TestClient
from core_app import core_app as app  
from routers.download import LOG_DIR  

client = TestClient(app)

def get_auth_header():
    response = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_download_battle_log():
    # 🔁 Use absolute path for file creation
    log_path = (LOG_DIR / "battle_log.txt").resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("Pikachu used Thunderbolt!")

    headers = get_auth_header()
    response = client.get("/download/log", headers=headers)

    assert response.status_code == 200
    assert "Thunderbolt" in response.text


def test_download_image():
    image_path = Path("uploads/images/test_image.png")
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(b"fake image content")

    headers = get_auth_header()
    response = client.get("/download/image/test_image.png", headers=headers)

    assert response.status_code == 200
    assert response.content == b"fake image content"


def test_download_missing_file():
    headers = get_auth_header()
    response = client.get("/download/image/does_not_exist.png", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Image not found."


def test_download_missing_log(monkeypatch):
    # ❌ Simulate missing log path
    monkeypatch.setattr("routers.download.LOG_DIR", Path("nonexistent_logs"))

    headers = get_auth_header()
    response = client.get("/download/log", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Battle log not found."
