# tests/auth/test_refresh_token.py

import pytest
from fastapi.testclient import TestClient
from core_app import core_app as app

client = TestClient(app)


# 🔐 Helper: Login and get both access + refresh tokens
def get_tokens():
    payload = {
        "username": "ashketchum",
        "password": "pikapika"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200, "Login failed — check credentials or route!"
    data = response.json()
    return data["access_token"], data["refresh_token"]


# 🧪 Main Test: Check token refresh works and rotates
def test_refresh_token_rotation():
    # 🎟️ Get initial tokens
    access_token, refresh_token = get_tokens()

    # ✅ Use refresh token to get new tokens (pass via Authorization header)
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("/auth/refresh-token", headers=headers)
    assert response.status_code == 200, "Refresh token request failed!"

    new_data = response.json()
    new_access = new_data["access_token"]
    new_refresh = new_data["refresh_token"]

    assert new_access != access_token, "Access token did not rotate!"
    assert new_refresh != refresh_token, "Refresh token did not rotate!"

    # ✅ Test new access token on protected route
    protected_headers = {"Authorization": f"Bearer {new_access}"}
    whoami_response = client.get("/auth/whoami", headers=protected_headers)
    assert whoami_response.status_code == 200, "New access token didn't work!"
    assert "ashketchum" in whoami_response.text, "Username not in /whoami response!"

    # ⛔ Reuse old refresh token (should fail if rotation is enforced)
    reuse_headers = {"Authorization": f"Bearer {refresh_token}"}
    reuse_attempt = client.post("/auth/refresh-token", headers=reuse_headers)
    assert reuse_attempt.status_code in (400, 401), "Old refresh token should be invalidated!"
