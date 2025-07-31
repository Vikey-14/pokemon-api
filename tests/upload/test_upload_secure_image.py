# ✅ tests/upload/test_upload_secure_image.py

import io
from fastapi.testclient import TestClient
from core_app import core_app as app  

client = TestClient(app)

# 🔐 Admin login for secure upload tests
def get_admin_auth_header():
    res = client.post("/auth/login", json={
        "username": "professoroak",
        "password": "pallet123"
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 🎒 Trainer login (not used in this test file, but ready for future)
def get_trainer_auth_header():
    res = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ✅ Secure image upload should succeed with valid image
def test_secure_image_upload_success():
    headers = get_admin_auth_header()
    file = io.BytesIO(b"fake image content")
    file.name = "secure_pikachu.png"

    response = client.post(
        "/upload/secure-image",
        files={"file": ("secure_pikachu.png", file, "image/png")},
        headers=headers
    )

    assert response.status_code == 200
    assert "Image Uploaded by professoroak" in response.text

# ❌ Secure upload should fail with invalid file type
def test_secure_image_upload_invalid_type():
    headers = get_admin_auth_header()
    file = io.BytesIO(b"not an image")
    file.name = "virus.exe"

    response = client.post(
        "/upload/secure-image",
        files={"file": ("virus.exe", file, "application/x-msdownload")},
        headers=headers
    )

    assert response.status_code == 400
    assert "Upload failed" in response.text

# ✅ Uploading multiple images should succeed
def test_multi_image_upload_success():
    headers = get_admin_auth_header()
    files = [
        ("files", ("img1.png", io.BytesIO(b"image1"), "image/png")),
        ("files", ("img2.jpg", io.BytesIO(b"image2"), "image/jpeg"))
    ]

    response = client.post("/upload/multi-image", files=files, headers=headers)
    assert response.status_code == 200
    assert "Uploaded by professoroak" in response.text
    assert "img1.png" in response.text or "img2.jpg" in response.text

# ❌ Multi-image upload should fail if all files are invalid
def test_multi_image_upload_all_invalid():
    headers = get_admin_auth_header()
    files = [
        ("files", ("bad.txt", io.BytesIO(b"text content"), "text/plain")),
        ("files", ("script.exe", io.BytesIO(b"malware"), "application/x-msdownload"))
    ]

    response = client.post("/upload/multi-image", files=files, headers=headers)
    assert response.status_code == 400
    assert "No valid image files uploaded" in response.text
