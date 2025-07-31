# tests/trainer/test_team.py

import pytest
from fastapi.testclient import TestClient
from core_app import core_app as app

client = TestClient(app)

# ✅ Credentials for login
LOGIN_CREDENTIALS = {
    "username": "ashketchum",
    "password": "pikapika"
}

# ✅ Helper to get a valid token
def get_token():
    response = client.post("/auth/login", json=LOGIN_CREDENTIALS)
    assert response.status_code == 200
    return response.json()["access_token"]

# 🔥 Use Bulbasaur (ID 1) from realistic_mock_pokedex for all actions
VALID_POKE_ID = 1
INVALID_POKE_ID = 999  # Definitely not in mock


# ✅ Add Pokémon to team
def test_add_pokemon_to_team():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/team/{VALID_POKE_ID}", headers=headers)
    assert response.status_code == 201
    assert "added" in response.json()["Message"].lower()


# ✅ Get current team
def test_get_current_team():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/team", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ✅ Add duplicate Pokémon
def test_add_duplicate_pokemon():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    # Add once
    client.post(f"/team/{VALID_POKE_ID}", headers=headers)
    # Try duplicate
    response = client.post(f"/team/{VALID_POKE_ID}", headers=headers)
    assert response.status_code == 409
    assert "already" in response.json()["detail"].lower()


# ✅ Remove Pokémon from team (FIXED: ensure it's first added)
def test_remove_pokemon_from_team():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 🔁 Step 1: Add the Pokémon to ensure it's present
    add_response = client.post(f"/team/{VALID_POKE_ID}", headers=headers)
    assert add_response.status_code == 201

    # ❌ Step 2: Now remove it
    remove_response = client.delete(f"/team/{VALID_POKE_ID}", headers=headers)
    assert remove_response.status_code == 200
    assert "removed" in remove_response.json()["Message"].lower()


# ✅ Try removing non-existent Pokémon
def test_remove_nonexistent_pokemon():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/team/{INVALID_POKE_ID}", headers=headers)
    assert response.status_code == 404
    assert "not in your team" in response.json()["detail"].lower()
