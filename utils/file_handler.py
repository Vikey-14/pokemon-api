import os
import json
import traceback
from typing import Dict, Union

# ✅ Unified file path for Pokédex
POKEDEX_PATH = os.path.join("data", "pokedex.json")

# ✅ Ensure the data directory exists
os.makedirs(os.path.dirname(POKEDEX_PATH), exist_ok=True)

def _fh_bc(event: str, **fields) -> None:
    try:
        parts = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
        print(f"[FH_BC] {event}" + (f" {parts}" if parts else ""), flush=True)
    except Exception as e:
        print(f"[FH_BC] {event} breadcrumb_error={type(e).__name__}:{e}", flush=True)


def load_pokedex() -> Dict[int, dict]:
    """
    Loads the Pokédex and returns keys as integers for reliable PATCH/DELETE access.
    """
    _fh_bc("LOAD_POKEDEX_ENTER")
    _fh_bc("LOAD_POKEDEX_PATH", path=POKEDEX_PATH, exists=os.path.exists(POKEDEX_PATH))

    if not os.path.exists(POKEDEX_PATH):
        _fh_bc("LOAD_POKEDEX_MISSING", path=POKEDEX_PATH)
        _log("❌ Pokédex file not found.")
        return {}

    try:
        with open(POKEDEX_PATH, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        _fh_bc(
            "LOAD_POKEDEX_AFTER_JSON",
            raw_type=type(raw_data).__name__,
            raw_len=len(raw_data) if hasattr(raw_data, "__len__") else None,
        )

        pokedex = {}

        if isinstance(raw_data, dict):
            for key_str, entry in raw_data.items():
                try:
                    _fh_bc("LOAD_POKEDEX_DICT_ITEM_BEGIN", key=key_str, entry=entry)

                    if not isinstance(entry, dict):
                        raise TypeError(f"Entry for key {key_str} is not a dict")

                    key_int = int(key_str)

                    fixed_entry = entry.copy()
                    fixed_entry["id"] = int(fixed_entry.get("id", key_int))  # 🔁 Ensure ID is int

                    pokedex[key_int] = fixed_entry

                    _fh_bc("LOAD_POKEDEX_DICT_ITEM_OK", key=key_str, normalized=fixed_entry)

                except Exception as e:
                    _fh_bc(
                        "LOAD_POKEDEX_DICT_ITEM_ERR",
                        key=key_str,
                        entry=entry,
                        err_type=type(e).__name__,
                        err=str(e),
                    )
                    raise

        elif isinstance(raw_data, list):
            for i, entry in enumerate(raw_data, start=1):
                try:
                    _fh_bc("LOAD_POKEDEX_LIST_ITEM_BEGIN", index=i, entry=entry)

                    if not isinstance(entry, dict):
                        raise TypeError(f"List entry at index {i} is not a dict")

                    fixed_entry = entry.copy()
                    fixed_entry["id"] = int(fixed_entry.get("id", i))

                    pokedex[i] = fixed_entry

                    _fh_bc("LOAD_POKEDEX_LIST_ITEM_OK", index=i, normalized=fixed_entry)

                except Exception as e:
                    _fh_bc(
                        "LOAD_POKEDEX_LIST_ITEM_ERR",
                        index=i,
                        entry=entry,
                        err_type=type(e).__name__,
                        err=str(e),
                    )
                    raise

        else:
            _fh_bc("LOAD_POKEDEX_INVALID_FORMAT", raw_type=type(raw_data).__name__)
            _log("❌ Invalid Pokédex format.")
            return {}

        _fh_bc("LOAD_POKEDEX_RETURN_OK", count=len(pokedex))
        _log(f"✅ Loaded {len(pokedex)} Pokémon.")
        return pokedex

    except Exception as e:
        _fh_bc(
            "LOAD_POKEDEX_ERR",
            err_type=type(e).__name__,
            err=str(e),
        )
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
