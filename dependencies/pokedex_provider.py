# 📦 dependencies/pokedex_provider.py

from utils.file_handler import load_pokedex
from config import settings
from custom_logger import error_logger

# 🔹 For /pokemon routes (string keys)
def get_pokedex_data():
    try:
        raw_pokedex = load_pokedex()
        formatted = {}

        for poke_id, entry in raw_pokedex.items():
            str_id = str(poke_id)  # 🔁 Force string key
            formatted[str_id] = {
                "name": entry.get("name"),
                "level": entry.get("level"),
                "ptype": entry.get("ptype"),
                "nickname": entry.get("nickname") or None,
                "id": int(entry.get("id", poke_id))  # Fallback if "id" missing
            }

        return formatted

    except Exception as e:
        if not settings.TESTING:
            error_logger.error(f"❌ CRASH in get_pokedex_data(): {e}", exc_info=True)
        raise


# 🔹 For /team routes (int keys)
def get_team_pokedex_data():
    try:
        raw_pokedex = load_pokedex()
        formatted = {}

        for poke_id, entry in raw_pokedex.items():
            int_id = int(poke_id)  # 🔁 Force int key
            formatted[int_id] = {
                "name": entry.get("name"),
                "level": entry.get("level"),
                "ptype": entry.get("ptype"),
                "nickname": entry.get("nickname") or None,
                "id": int(entry.get("id", poke_id))
            }

        return formatted

    except Exception as e:
        if not settings.TESTING:
            error_logger.error(f"❌ CRASH in get_team_pokedex_data(): {e}", exc_info=True)
        raise


# 🔐 Clean import control
__all__ = ["get_pokedex_data", "get_team_pokedex_data"]
