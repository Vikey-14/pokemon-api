import os
import json
import traceback
from typing import Dict, Union

# ✅ Unified file path for Pokédex
POKEDEX_PATH = os.path.join("data", "pokedex.json")

# ✅ Ensure the data directory exists
os.makedirs(os.path.dirname(POKEDEX_PATH), exist_ok=True)

def load_pokedex() -> Dict[int, dict]:
    """
    Loads the Pokédex and returns keys as integers for reliable PATCH/DELETE access.
    """
    if not os.path.exists(POKEDEX_PATH):
        _log("❌ Pokédex file not found.")
        return {}

    try:
        with open(POKEDEX_PATH, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            pokedex = {}

            if isinstance(raw_data, dict):
                for key_str, entry in raw_data.items():
                    key_int = int(key_str)
                    entry["id"] = int(entry.get("id", key_int))  # 🔁 Ensure ID is int
                    pokedex[key_int] = entry
            elif isinstance(raw_data, list):
                for i, entry in enumerate(raw_data, start=1):
                    entry["id"] = int(entry.get("id", i))
                    pokedex[i] = entry
            else:
                _log("❌ Invalid Pokédex format.")
                return {}

            _log(f"✅ Loaded {len(pokedex)} Pokémon.")
            return pokedex

    except Exception as e:
        _log(f"❌ Error loading Pokédex: {e}")
        _log(traceback.format_exc())
        return {}

def save_pokedex(data: Union[Dict[int, dict], Dict]):
    """
    Saves the Pokédex to disk with:
    - Keys saved as strings in JSON
    - id field kept as integer inside each entry
    - nickname field removed if None
    """
    try:
        # ✅ Step 1: Normalize keys to int
        normalized = {int(k): v for k, v in data.items()}

        # ✅ Step 2: Clean entries
        for poke_id, entry in normalized.items():
            entry["id"] = int(entry.get("id", poke_id))  # 🔁 Ensure 'id' field is int
            if entry.get("nickname") is None:
                entry.pop("nickname", None)

        # ✅ Step 3: Convert keys to strings for JSON save
        str_keys = {str(k): v for k, v in normalized.items()}

        # ✅ Step 4: Save to file
        with open(POKEDEX_PATH, "w", encoding="utf-8") as file:
            json.dump(str_keys, file, indent=4, ensure_ascii=False)

        _log(f"💾 Pokédex saved to: {POKEDEX_PATH}")

    except Exception as e:
        _log(f"❌ Error in save_pokedex: {e}")
        _log(traceback.format_exc())
        raise

# 🔧 Internal logger (quiet during pytest)
def _log(message: str):
    if os.getenv("TESTING") != "1":
        print(message)
