# ✅ tests/permissions/test_admin_only.py

import io
from fastapi.testclient import TestClient
from core_app import core_app as app  

client = TestClient(app)

# 🔐 Login as Admin (Professor Oak)
def get_admin_auth_header():
    res = client.post("/auth/login", json={
        "username": "professoroak",
        "password": "pallet123"
    })
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

# 🧢 Login as Trainer (Ash Ketchum)
def get_trainer_auth_header():
    res = client.post("/auth/login", json={
        "username": "ashketchum",
        "password": "pikapika"
    })
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

# ✅ Admin should be allowed
def test_admin_access_allowed():
    headers = get_admin_auth_header()
    file = io.BytesIO(b"fake image content")
    file.name = "ok.png"

    response = client.post(
        "/upload/secure-image",
        files={"file": ("ok.png", file, "image/png")},
        headers=headers
    )

    assert response.status_code == 200
    assert "Uploaded by professoroak" in response.text

# ❌ Trainer should be forbidden
def test_trainer_access_forbidden():
    headers = get_trainer_auth_header()
    file = io.BytesIO(b"fake image content")
    file.name = "fail.png"

    response = client.post(
        "/upload/secure-image",
        files={"file": ("fail.png", file, "image/png")},
        headers=headers
    )

    assert response.status_code == 403
    assert "Forbidden" in response.text

# ❌ No token should get 403 (FastAPI's HTTPBearer behavior)
def test_no_auth_access_denied():
    file = io.BytesIO(b"fake image content")
    file.name = "notoken.png"

    response = client.post(
        "/upload/secure-image",
        files={"file": ("notoken.png", file, "image/png")}
    )

    assert response.status_code == 403  # 🔁 Updated from 401 → 403
    assert "Not authenticated" in response.text or "credentials" in response.text
