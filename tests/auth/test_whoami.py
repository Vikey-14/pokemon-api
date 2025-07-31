# tests/auth/test_whoami.py

import pytest
from fastapi.testclient import TestClient
from core_app import core_app as app

client = TestClient(app)

# 🧪 Helper: Login and get valid access token
def get_access_token():
    payload = {
        "username": "ashketchum",
        "password": "pikapika"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200, "Login failed — check credentials!"
    return response.json()["access_token"]

# ✅ Test valid access token on /whoami
def test_whoami_with_valid_token():
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/auth/whoami", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "ashketchum" in data["message"]
    assert "trainer" in data["message"]

# ❌ Test missing token
def test_whoami_without_token():
    response = client.get("/auth/whoami")
    assert response.status_code == 403  # HTTPBearer requires token
    assert "Not authenticated" in response.text

# ❌ Test invalid/malformed token
def test_whoami_with_invalid_token():
    headers = {"Authorization": "Bearer faketoken123"}
    response = client.get("/auth/whoami", headers=headers)
    assert response.status_code == 401
    assert "Invalid token" in response.text
