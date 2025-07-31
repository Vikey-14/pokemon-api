import os
import json
from typing import Dict, Any
import traceback

# ✅ Consistent path to team data file
TEAM_FILE_PATH = os.path.join("data", "team_data.json")

# ✅ Ensure the 'data' folder exists
os.makedirs(os.path.dirname(TEAM_FILE_PATH), exist_ok=True)


def load_team() -> Dict[str, dict]:
    """
    Load the trainer's team from team_data.json.
    Returns an empty dict if file is missing or corrupted.
    """
    if not os.path.exists(TEAM_FILE_PATH):
        _log("📭 Team file not found.")
        return {}

    try:
        with open(TEAM_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

            if not isinstance(data, dict):
                _log("❌ Team file format is invalid.")
                return {}

            _log(f"✅ Loaded team with {len(data)} Pokémon.")
            return data

    except json.JSONDecodeError as e:
        _log(f"❌ JSON decode error in team file: {e}")
        _log(traceback.format_exc())
        return {}
    except Exception as e:
        _log(f"❌ Error reading team file: {e}")
        _log(traceback.format_exc())
        return {}


def save_team(team: Dict[str, Any]) -> None:
    """
    Save the current team to team_data.json with pretty formatting.
    """
    try:
        with open(TEAM_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(team, f, indent=4, ensure_ascii=False)
        _log("💾 Team saved successfully.")
    except Exception as e:
        _log(f"❌ Error saving team file: {e}")
        _log(traceback.format_exc())
        raise  

# 🔕 Test-safe logging toggle
def _log(message: str):
    if os.getenv("TESTING") != "1":
        print(message)
