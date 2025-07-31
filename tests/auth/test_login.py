# tests/auth/test_login.py

def test_login_success(test_client):
    payload = {
        "username": "ashketchum",
        "password": "pikapika"
    }
    response = test_client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(test_client):
    payload = {
        "username": "ashketchum",
        "password": "wrongpass"
    }
    response = test_client.post("/auth/login", json=payload)
    assert response.status_code == 401
