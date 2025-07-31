import pytest
import os
import shutil
import sys
import json

# ✅ Enable test mode globally
os.environ["TESTING"] = "1"

# 🛠️ Ensure project root is discoverable (important when running from /tests)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🧠 Core state reset helpers
from utils.file_handler import save_pokedex
from utils.team_handler import save_team
from auth.hybrid_auth import refresh_token_store
from fastapi.testclient import TestClient
from core_app import core_app as app

# 📁 Define folders that should be cleaned before each test
CLEANUP_FOLDERS = [
    "uploads",
    "gallery"
    # 🛑 Do NOT include "logs" — handled separately to preserve prod logs
]

@pytest.fixture(autouse=True)
def clean_everything_before_each_test():
    """
    Automatically runs before every test.
    Resets pokedex, team, token store, and selected folders.
    Avoids touching production logs.
    """
    # 🔁 Skip cleanup if SKIP_RESET=1 is set in the environment
    if os.getenv("SKIP_RESET") == "1":
        return

    # ✅ Reset Pokédex and Team files (safe empty dicts)
    save_pokedex({})
    save_team({})

    # ✅ Clear in-memory refresh token store
    refresh_token_store.clear()

    # ✅ Clean up folders (recreate empty)
    for folder in CLEANUP_FOLDERS:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

    # ✅ Ensure pokedex.json and team_data.json are valid empty JSON
    os.makedirs("data", exist_ok=True)
    with open("data/pokedex.json", "w", encoding="utf-8") as f:
        f.write("{}\n")
    with open("data/team_data.json", "w", encoding="utf-8") as f:
        f.write("{}\n")

    # ✅ Clean test logs (but don't touch production logs)
    os.makedirs("logs", exist_ok=True)
    test_log_path = "logs/test_info.log"
    if os.path.exists(test_log_path):
        try:
            os.remove(test_log_path)
        except PermissionError:
            print(f"⚠️ Could not delete {test_log_path} — is it still open?")


# ✅ Auto-seed Pokédex for each test
@pytest.fixture(autouse=True)
def seed_pokedex_before_tests():
    """
    Seeds the pokedex.json with at least one valid Pokémon (Bulbasaur) before each test.
    Ensures /team/1 and /pokemon/1 routes are testable.
    """
    test_pokemon = {
        "1": {
            "name": "Bulbasaur",
            "level": 5,
            "ptype": "Grass",
            "nickname": None,
            "id": 1
        }
    }
    save_pokedex(test_pokemon)


# ✅ Provide reusable test client
@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)
