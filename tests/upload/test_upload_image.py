# tests/upload/test_upload_image.py

import io
from fastapi.testclient import TestClient
from core_app import core_app as app   # ✅ Use the real app (core_app imported by main)

client = TestClient(app)

# 🔐 Helper to login and fetch token
def get_auth_header():
    response = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


# ✅ Test: Single image upload
def test_upload_single_image_success():
    file = io.BytesIO(b"fake image content")
    file.name = "pikachu.png"

    headers = get_auth_header()
    response = client.post(
        "/upload/image",
        files={"file": ("pikachu.png", file, "image/png")},
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Image uploaded!"
    assert "filename" in response.json()


# ✅ Test: Multiple image upload
def test_upload_multiple_images_success():
    file1 = io.BytesIO(b"image1")
    file1.name = "bulbasaur.png"

    file2 = io.BytesIO(b"image2")
    file2.name = "charmander.jpg"

    headers = get_auth_header()
    response = client.post(
        "/upload/images",
        files=[
            ("files", ("bulbasaur.png", file1, "image/png")),
            ("files", ("charmander.jpg", file2, "image/jpeg")),
        ],
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["message"].startswith("2 image")
    assert "filenames" in response.json()
    assert len(response.json()["filenames"]) == 2


# 🚫 Test: Invalid file type
def test_upload_invalid_file_type():
    file = io.BytesIO(b"this is not an image")
    file.name = "not_a_pokemon.txt"

    headers = get_auth_header()
    response = client.post(
        "/upload/image",
        files={"file": ("not_a_pokemon.txt", file, "text/plain")},
        headers=headers
    )

    assert response.status_code in [400, 422]
