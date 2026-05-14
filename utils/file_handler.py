import os
import json
import traceback
from typing import Dict, Union, Any

from utils.db_json_store import load_json_document, save_json_document, storage_debug


# ✅ Old local fallback path
# Used only when DATABASE_URL is missing or during local/test mode.
POKEDEX_PATH = os.path.join("data", "pokedex.json")

# ✅ Ensure local fallback directory exists
os.makedirs(os.path.dirname(POKEDEX_PATH), exist_ok=True)


def _log(message: str):
    """
    Quiet during pytest, visible in Render/local logs otherwise.
    """
    if os.getenv("TESTING") != "1":
        print(message, flush=True)


def _fh_bc(event: str, **fields) -> None:
    """
    Pokédex storage breadcrumb logger.

    These logs prove:
    - whether Neon DB is active
    - whether local JSON fallback is being used
    - what nickname values were loaded/saved
    - whether save verification succeeded
    """
    try:
        parts = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
        _log(f"[FH_BC] {event}" + (f" {parts}" if parts else ""))
    except Exception as e:
        _log(f"[FH_BC] {event} breadcrumb_error={type(e).__name__}:{e}")


def _normalize_pokedex(raw_data: Any) -> Dict[int, dict]:
    """
    Convert raw Pokédex data into the format the existing routes expect:

    {
        1: {"name": "...", "level": ..., "ptype": "...", "id": 1}
    }

    Supports:
    - dict from JSON file
    - dict from Neon JSONB
    - old list-style fallback
    """
    pokedex: Dict[int, dict] = {}

    if raw_data is None:
        _fh_bc("NORMALIZE_POKEDEX_NONE")
        return {}

    if isinstance(raw_data, dict):
        for key_str, entry in raw_data.items():
            try:
                _fh_bc("NORMALIZE_DICT_ITEM_BEGIN", key=key_str, entry=entry)

                key_int = int(key_str)

                if not isinstance(entry, dict):
                    raise TypeError(f"Pokédex entry {key_str} is not a dict")

                fixed_entry = dict(entry)
                fixed_entry["id"] = int(fixed_entry.get("id", key_int))

                pokedex[key_int] = fixed_entry

                _fh_bc("NORMALIZE_DICT_ITEM_OK", key=key_str, normalized=fixed_entry)

            except Exception as e:
                _fh_bc(
                    "NORMALIZE_DICT_ITEM_ERR",
                    key=key_str,
                    entry=entry,
                    err_type=type(e).__name__,
                    err=str(e),
                )
                raise

    elif isinstance(raw_data, list):
        for i, entry in enumerate(raw_data, start=1):
            try:
                _fh_bc("NORMALIZE_LIST_ITEM_BEGIN", index=i, entry=entry)

                if not isinstance(entry, dict):
                    raise TypeError(f"Pokédex list entry {i} is not a dict")

                fixed_entry = dict(entry)
                fixed_entry["id"] = int(fixed_entry.get("id", i))

                pokedex[i] = fixed_entry

                _fh_bc("NORMALIZE_LIST_ITEM_OK", index=i, normalized=fixed_entry)

            except Exception as e:
                _fh_bc(
                    "NORMALIZE_LIST_ITEM_ERR",
                    index=i,
                    entry=entry,
                    err_type=type(e).__name__,
                    err=str(e),
                )
                raise

    else:
        raise TypeError(f"Invalid Pokédex format: {type(raw_data).__name__}")

    _fh_bc(
        "NORMALIZE_POKEDEX_OK",
        count=len(pokedex),
        nicknames={str(pid): entry.get("nickname") for pid, entry in pokedex.items()},
    )

    return pokedex


def _load_pokedex_from_file() -> Dict[int, dict]:
    """
    Old local JSON loader.

    This is now used only as:
    - local fallback when DATABASE_URL is missing
    - initial seed source when Neon DB row does not exist yet
    """
    _fh_bc(
        "FILE_LOAD_POKEDEX_ENTER",
        path=POKEDEX_PATH,
        exists=os.path.exists(POKEDEX_PATH),
    )

    if not os.path.exists(POKEDEX_PATH):
        _fh_bc("FILE_LOAD_POKEDEX_MISSING", path=POKEDEX_PATH)
        return {}

    try:
        with open(POKEDEX_PATH, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        pokedex = _normalize_pokedex(raw_data)

        _fh_bc(
            "FILE_LOAD_POKEDEX_OK",
            count=len(pokedex),
            nicknames={str(pid): entry.get("nickname") for pid, entry in pokedex.items()},
        )

        return pokedex

    except Exception as e:
        _fh_bc(
            "FILE_LOAD_POKEDEX_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        return {}


def _save_pokedex_to_file(data: Dict[int, dict]) -> None:
    """
    Old local JSON saver.

    Used only when DATABASE_URL is missing.
    In Render production, we do NOT want this path.
    """
    try:
        normalized = {}

        for raw_key, raw_entry in data.items():
            poke_id = int(raw_key)

            if not isinstance(raw_entry, dict):
                raise TypeError(f"Pokédex entry {raw_key} is not a dict")

            entry = dict(raw_entry)
            entry["id"] = int(entry.get("id", poke_id))

            # ✅ Keep old clean behavior:
            # If nickname is None/blank, don't store it.
            # If nickname is real, like "bulby", keep it.
            if entry.get("nickname") is None or entry.get("nickname") == "":
                entry.pop("nickname", None)

            normalized[str(poke_id)] = entry

        with open(POKEDEX_PATH, "w", encoding="utf-8") as file:
            json.dump(normalized, file, indent=4, ensure_ascii=False)

        _fh_bc(
            "FILE_SAVE_POKEDEX_OK",
            path=POKEDEX_PATH,
            count=len(normalized),
            nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
        )

    except Exception as e:
        _fh_bc(
            "FILE_SAVE_POKEDEX_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        raise


def load_pokedex() -> Dict[int, dict]:
    """
    Main Pokédex loader used by the app.

    Render production:
        DATABASE_URL present → load from Neon PostgreSQL.

    Local/dev/test:
        DATABASE_URL missing or TESTING=1 → load from data/pokedex.json.
    """
    _fh_bc("LOAD_POKEDEX_ENTER", storage=storage_debug())

    try:
        raw_data = load_json_document(
            key="pokedex",
            fallback_loader=_load_pokedex_from_file,
            expected_empty={},
        )

        pokedex = _normalize_pokedex(raw_data)

        _fh_bc(
            "LOAD_POKEDEX_RETURN_OK",
            count=len(pokedex),
            storage=storage_debug(),
            nicknames={str(pid): entry.get("nickname") for pid, entry in pokedex.items()},
        )

        return pokedex

    except Exception as e:
        _fh_bc(
            "LOAD_POKEDEX_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
            storage=storage_debug(),
        )
        raise


def save_pokedex(data: Union[Dict[int, dict], Dict[Any, dict]]):
    """
    Main Pokédex saver used by the app.

    If DATABASE_URL exists:
        Saves to Neon.

    If DATABASE_URL is missing:
        Saves to local JSON fallback.

    This preserves old local behavior while making Render persistent.
    """
    _fh_bc(
        "SAVE_POKEDEX_ENTER",
        incoming_type=type(data).__name__,
        incoming_len=len(data) if hasattr(data, "__len__") else None,
        storage=storage_debug(),
    )

    try:
        normalized: Dict[str, dict] = {}

        for raw_key, raw_entry in data.items():
            poke_id = int(raw_key)

            if not isinstance(raw_entry, dict):
                raise TypeError(f"Pokédex entry {raw_key} is not a dict")

            entry = dict(raw_entry)
            entry["id"] = int(entry.get("id", poke_id))

            # ✅ Keep old clean behavior:
            # None/blank nickname is removed.
            # Real nickname survives.
            if entry.get("nickname") is None or entry.get("nickname") == "":
                entry.pop("nickname", None)

            normalized[str(poke_id)] = entry

        _fh_bc(
            "SAVE_POKEDEX_NORMALIZED",
            count=len(normalized),
            nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
            storage=storage_debug(),
        )

        saved_to_db = save_json_document("pokedex", normalized)

        if saved_to_db:
            _fh_bc(
                "SAVE_POKEDEX_DB_OK",
                count=len(normalized),
                nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
                storage=storage_debug(),
            )

            # ✅ Immediate verification from Neon.
            verify_raw = load_json_document(
                key="pokedex",
                fallback_loader=_load_pokedex_from_file,
                expected_empty={},
            )
            verify_pokedex = _normalize_pokedex(verify_raw)

            _fh_bc(
                "SAVE_POKEDEX_DB_VERIFY_OK",
                count=len(verify_pokedex),
                verify_nicknames={
                    str(pid): entry.get("nickname")
                    for pid, entry in verify_pokedex.items()
                },
                storage=storage_debug(),
            )

            return

        # ✅ Local fallback only when DB is disabled.
        _fh_bc("SAVE_POKEDEX_FILE_FALLBACK_BEGIN", storage=storage_debug())
        _save_pokedex_to_file({int(k): v for k, v in normalized.items()})

    except Exception as e:
        _fh_bc(
            "SAVE_POKEDEX_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
            storage=storage_debug(),
        )
        raise