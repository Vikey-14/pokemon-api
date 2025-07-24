from fastapi.testclient import TestClient
from post_auto_id_generation import app  # 🔁 Replace this with your actual file name (without `.py`)

client = TestClient(app)

def test_create_pokemon():
    response = client.post("/pokemon", json={
        "name": "Squirtle",
        "Type": "Water",
        "level": 5
    })
    assert response.status_code == 200
    assert response.json()["Message"] == "Pokemon Added!"
    assert response.json()["Data"]["Type"] == "Water"
