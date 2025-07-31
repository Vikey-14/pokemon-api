from fastapi.testclient import TestClient
from core_app import core_app as app

client = TestClient(app)

# 👤 Admin credentials
admin_login = {
    "username": "professoroak",
    "password": "pallet123"
}

def test_crud_pokemon():
    # 🔐 Step 1 – Login and get access token
    res = client.post("/auth/login", json=admin_login)
    assert res.status_code == 200
    access_token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 🧪 Step 2 – Add a new Pokémon
    new_pokemon = {
        "poke_name": "Garchomp",
        "level": 62,
        "ptype": "Dragon"
    }
    res = client.post("/pokemon/", json=new_pokemon, headers=headers)
    assert res.status_code == 201
    data = res.json()["Data"]
    assert data["name"] == "Garchomp"
    assert data["level"] == 62
    assert data["ptype"] == "Dragon"
    created_id = data["id"]  # 🔢 Should already be an integer

    # 🧪 Step 3 – Get all Pokémon
    res = client.get("/pokemon/", headers=headers)
    assert res.status_code == 200
    all_pokemon = res.json()
    names = [p["name"] for p in all_pokemon]
    assert "Garchomp" in names

    # 🧪 Step 4 – Update Garchomp
    updated_data = {
        "level": 70,
        "ptype": "Dragon/Ground"
    }
    res = client.patch(f"/pokemon/{created_id}", json=updated_data, headers=headers)
    assert res.status_code == 200
    updated = res.json()["Data"]
    assert updated["level"] == 70
    assert updated["ptype"] == "Dragon/Ground"

    # 🧪 Step 5 – Delete Garchomp
    res = client.delete(f"/pokemon/{created_id}", headers=headers)
    assert res.status_code == 200
    assert "Garchomp deleted" in res.json()["Message"]

    # 🧪 Step 6 – Confirm Garchomp is gone
    res = client.get("/pokemon/", headers=headers)
    assert res.status_code == 200
    remaining = res.json()
    names_after = [p["name"] for p in remaining]
    assert "Garchomp" not in names_after
