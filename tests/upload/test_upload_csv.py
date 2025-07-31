# tests/upload/test_upload_csv.py

import pytest
from fastapi.testclient import TestClient
from core_app import core_app as app  
from io import BytesIO

client = TestClient(app)

# ✅ Admin login credentials
ADMIN_CREDENTIALS = {
    "username": "professoroak",
    "password": "pallet123"
}

# 🧠 In-memory mock Pokédex for test isolation
mock_pokedex_store = {}

def mock_load_pokedex():
    return mock_pokedex_store.copy()

def mock_save_pokedex(new_data):
    global mock_pokedex_store
    mock_pokedex_store = new_data.copy()

# 🔐 Get access token for admin
def get_admin_token():
    response = client.post("/auth/login", json=ADMIN_CREDENTIALS)
    assert response.status_code == 200
    return response.json()["access_token"]

# ✅ Test 1: Upload valid CSV
def test_upload_valid_csv(monkeypatch):
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 🧪 Inject mocked handlers into upload_csv route
    monkeypatch.setattr("routers.upload_csv.load_pokedex", mock_load_pokedex)
    monkeypatch.setattr("routers.upload_csv.save_pokedex", mock_save_pokedex)

    csv_content = b"""name,type,level,nickname
Bulbasaur,Grass/Poison,5,bulba
Charmander,Fire,7,char
"""

    response = client.post(
        "/upload/csv",
        headers=headers,
        files={"file": ("pokemon.csv", BytesIO(csv_content), "text/csv")}
    )

    assert response.status_code == 201
    assert response.json()["added"] == ["Bulbasaur", "Charmander"]
    assert "message" in response.json()

# ❌ Test 2: Upload non-CSV file (e.g. TXT file)
def test_upload_non_csv():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    txt_file = b"This is not a CSV"

    response = client.post(
        "/upload/csv",
        headers=headers,
        files={"file": ("bad.txt", BytesIO(txt_file), "text/plain")}
    )

    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()

# ❌ Test 3: Upload invalid UTF-8 encoded file
def test_upload_bad_encoding():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Corrupted binary content (not UTF-8)
    bad_bytes = b"\xff\xfe\x00\x00"

    response = client.post(
        "/upload/csv",
        headers=headers,
        files={"file": ("corrupt.csv", BytesIO(bad_bytes), "text/csv")}
    )

    assert response.status_code == 400
    assert "utf-8" in response.json()["detail"].lower()

# 🔒 Test 4: Upload as trainer (should be forbidden)
def test_upload_as_trainer():
    trainer_creds = {
        "username": "ashketchum",
        "password": "pikapika"
    }
    response = client.post("/auth/login", json=trainer_creds)
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    csv_content = b"name,type,level,nickname\nPidgey,Normal/Flying,4,birdy"

    response = client.post(
        "/upload/csv",
        headers=headers,
        files={"file": ("trainer.csv", BytesIO(csv_content), "text/csv")}
    )

    assert response.status_code == 403
    assert response.json()["detail"].lower() in ["forbidden", "not authorized"]
