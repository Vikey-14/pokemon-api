# tests/upload/test_upload_info.py

import io
from fastapi.testclient import TestClient
from core_app import core_app as app 
import pytest

client = TestClient(app)

# 🔐 Helper to fetch valid token
def get_auth_header():
    response = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ✅ Test saving a valid text file
def test_save_text_file():
    file = io.BytesIO(b"Hello from FastAPI!")
    file.name = "hello.txt"

    headers = get_auth_header()
    response = client.post(
        "/upload/save",
        files={"file": (file.name, file, "text/plain")},
        headers=headers
    )
    assert response.status_code == 200
    assert "File saved" in response.json()["message"]
    assert response.json()["original_name"] == "hello.txt"


# ✅ Test previewing a valid CSV file
def test_preview_csv_file():
    file = io.BytesIO(b"name,level,type\nPikachu,25,Electric")
    file.name = "data.csv"

    headers = get_auth_header()
    response = client.post(
        "/upload/preview",
        files={"file": (file.name, file, "text/csv")},
        headers=headers
    )
    assert response.status_code == 200
    assert "preview" in response.json()
    assert response.json()["filename"] == "data.csv"


# ✅ Test previewing an image (no content preview expected)
def test_preview_image_file():
    file = io.BytesIO(b"fake image data")
    file.name = "test.png"

    headers = get_auth_header()
    response = client.post(
        "/upload/preview",
        files={"file": (file.name, file, "image/png")},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"].startswith("🖼️ Image uploaded")


# ✅ Test invalid file type (e.g., .exe)
def test_upload_invalid_file_type():
    file = io.BytesIO(b"binary data")
    file.name = "malicious.exe"

    headers = get_auth_header()
    response = client.post(
        "/upload/save",
        files={"file": (file.name, file, "application/octet-stream")},
        headers=headers
    )
    assert response.status_code in [400, 415]
    assert "not allowed" in str(response.json().get("detail", "")).lower()
