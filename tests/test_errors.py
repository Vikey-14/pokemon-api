# ✅ tests/test_errors.py

from fastapi.testclient import TestClient
from core_app import core_app as app  

client = TestClient(app)

# 🔐 Trainer login
def get_trainer_auth_header():
    res = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

# ❌ 401 Unauthorized — No token provided
def test_error_unauthenticated():
    response = client.get("/gallery")  # Protected route without token
    assert response.status_code == 401  # ✅ Fixed: 403 → 401
    assert "Not authenticated" in response.text or "credentials" in response.text

# ❌ 403 Forbidden — Trainer accessing admin route
def test_error_forbidden_access():
    headers = get_trainer_auth_header()
    response = client.post("/upload/secure-image", headers=headers, files={})
    assert response.status_code == 403
    assert "Forbidden" in response.text

# ❌ 404 Not Found — Invalid route
def test_error_route_not_found():
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "Not Found" in response.text or "not found" in response.text.lower()

# ❌ 422 Unprocessable Entity — Missing password in login
def test_error_unprocessable_entity():
    response = client.post("/auth/login", json={"username": "ashketchum"})
    assert response.status_code == 422
    assert "Field required" in response.text  # ✅ Fixed assertion
