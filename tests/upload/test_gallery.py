import os
from fastapi.testclient import TestClient
from core_app import core_app as app  

client = TestClient(app)

# 🔐 Trainer login helper (auth not required to test logic, but used for real route)
def get_trainer_auth_header():
    res = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ✅ Test 1: Gallery has images
def test_gallery_success_with_images(monkeypatch):
    def mock_exists(path):
        return True  # Pretend gallery folder exists

    def mock_listdir(path):
        return ["bulbasaur.png", "charmander.jpg"]

    monkeypatch.setattr(os.path, "exists", mock_exists)
    monkeypatch.setattr(os, "listdir", mock_listdir)

    headers = get_trainer_auth_header()
    response = client.get("/gallery", headers=headers)

    assert response.status_code == 200
    assert "bulbasaur.png" in response.text
    assert "charmander.jpg" in response.text
    assert "Gallery" in response.text


# ✅ Test 2: Gallery folder exists but is empty
def test_gallery_empty(monkeypatch):
    def mock_exists(path):
        return True  # Gallery exists

    def mock_listdir(path):
        return []  # Empty folder

    monkeypatch.setattr(os.path, "exists", mock_exists)
    monkeypatch.setattr(os, "listdir", mock_listdir)

    headers = get_trainer_auth_header()
    response = client.get("/gallery", headers=headers)

    assert response.status_code == 200
    assert "No Pokémon images have been uploaded yet." in response.text


# ✅ Test 3: Gallery folder doesn't exist at all
def test_gallery_no_folder(monkeypatch):
    def mock_exists(path):
        return False  # Pretend folder is missing

    monkeypatch.setattr(os.path, "exists", mock_exists)

    headers = get_trainer_auth_header()
    response = client.get("/gallery", headers=headers)

    assert response.status_code == 200
    assert "No images found" in response.text or "No Pokémon images" in response.text


# ✅ Test 4: Access without token
def test_gallery_unauthorized():
    response = client.get("/gallery")

    assert response.status_code == 401
    assert "Not authenticated" in response.text or "credentials" in response.text
