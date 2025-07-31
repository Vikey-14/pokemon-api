# tests/upload/test_upload_csv_validated.py

import pytest
from fastapi.testclient import TestClient
from core_app import core_app as app  
from io import BytesIO
from unittest.mock import patch

client = TestClient(app)

# 🔐 Admin login credentials
LOGIN_CREDENTIALS = {"username": "professoroak", "password": "pallet123"}

# ✅ Get token
def get_admin_token():
    response = client.post("/auth/login", json=LOGIN_CREDENTIALS)
    assert response.status_code == 200
    return response.json()["access_token"]

# 🧪 In-memory Pokédex mock
mock_pokedex = {}

# ✅ Test CSV with valid + bad rows
@patch("routers.upload_csv_validated.load_pokedex", return_value=mock_pokedex)
@patch("routers.upload_csv_validated.save_pokedex")
def test_validated_csv_upload(mock_save, mock_load):
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    csv_content = b"""id,name,type,level
1,Pikachu,Electric,12
2,,Fire,20
3,Charmander,Fire,3
1,Duplicate,Normal,10
4,Bulbasaur,Grass/Poison,55
"""

    response = client.post(
        "/upload/csv-import",
        headers=headers,
        files={"file": ("validated.csv", BytesIO(csv_content), "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["added"] == 2
    assert data["duplicates_skipped"] == 1
    assert data["failed_rows"] == 2
    errors = [d["error"] for d in data["details"]]
    assert any("Missing name or type" in e for e in errors)
    assert any("Invalid level" in e for e in errors)
    assert any("Duplicate ID" in e for e in errors)

# 🔐 Ensure only admins can upload
def test_upload_requires_admin():
    csv_content = b"id,name,type,level\n10,Mew,Psychic,99"
    response = client.post(
        "/upload/csv-import",
        files={"file": ("mew.csv", BytesIO(csv_content), "text/csv")}
    )
    assert response.status_code == 403 
