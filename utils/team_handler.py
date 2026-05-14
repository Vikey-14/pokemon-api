import os
import json
from typing import Dict, Any
import traceback

from utils.db_json_store import load_json_document, save_json_document, storage_debug


# ✅ Old local fallback path
# Used only when DATABASE_URL is missing or during local/test mode.
TEAM_FILE_PATH = os.path.join("data", "team_data.json")

# ✅ Ensure the local fallback folder exists
os.makedirs(os.path.dirname(TEAM_FILE_PATH), exist_ok=True)


def _log(message: str):
    """
    Quiet during pytest, visible in Render/local logs otherwise.
    """
    if os.getenv("TESTING") != "1":
        print(message, flush=True)


def _team_bc(event: str, **fields) -> None:
    """
    Team storage breadcrumb logger.

    These logs prove:
    - whether Neon DB is active
    - whether local JSON fallback is being used
    - what team data was loaded/saved
    - whether save verification succeeded
    """
    try:
        parts = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
        _log(f"[TEAM_BC] {event}" + (f" {parts}" if parts else ""))
    except Exception as e:
        _log(f"[TEAM_BC] {event} breadcrumb_error={type(e).__name__}:{e}")


def _normalize_team(raw_data: Any) -> Dict[str, dict]:
    """
    Convert raw team data into the format existing team routes expect:

    {
        "1": {"name": "...", "level": ..., "ptype": "..."}
    }

    Team keys stay as strings because many team routes usually use string IDs.
    """
    if raw_data is None:
        _team_bc("NORMALIZE_TEAM_NONE")
        return {}

    if not isinstance(raw_data, dict):
        raise TypeError(f"Invalid team format: {type(raw_data).__name__}")

    normalized: Dict[str, dict] = {}

    for raw_key, raw_entry in raw_data.items():
        try:
            _team_bc("NORMALIZE_TEAM_ITEM_BEGIN", key=raw_key, entry=raw_entry)

            if not isinstance(raw_entry, dict):
                raise TypeError(f"Team entry {raw_key} is not a dict")

            entry = dict(raw_entry)

            # ✅ Keep key as string for compatibility with current team routes.
            normalized[str(raw_key)] = entry

            _team_bc(
                "NORMALIZE_TEAM_ITEM_OK",
                key=raw_key,
                normalized=entry,
            )

        except Exception as e:
            _team_bc(
                "NORMALIZE_TEAM_ITEM_ERR",
                key=raw_key,
                entry=raw_entry,
                err_type=type(e).__name__,
                err=str(e),
            )
            raise

    _team_bc(
        "NORMALIZE_TEAM_OK",
        count=len(normalized),
        nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
    )

    return normalized


def _load_team_from_file() -> Dict[str, dict]:
    """
    Old local team JSON loader.

    This is now used only as:
    - local fallback when DATABASE_URL is missing
    - initial seed source when Neon DB row does not exist yet
    """
    _team_bc(
        "FILE_LOAD_TEAM_ENTER",
        path=TEAM_FILE_PATH,
        exists=os.path.exists(TEAM_FILE_PATH),
    )

    if not os.path.exists(TEAM_FILE_PATH):
        _team_bc("FILE_LOAD_TEAM_MISSING", path=TEAM_FILE_PATH)
        return {}

    try:
        with open(TEAM_FILE_PATH, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        team = _normalize_team(raw_data)

        _team_bc(
            "FILE_LOAD_TEAM_OK",
            count=len(team),
            nicknames={pid: entry.get("nickname") for pid, entry in team.items()},
        )

        return team

    except json.JSONDecodeError as e:
        _team_bc(
            "FILE_LOAD_TEAM_JSON_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        return {}

    except Exception as e:
        _team_bc(
            "FILE_LOAD_TEAM_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        return {}


def _save_team_to_file(team: Dict[str, Any]) -> None:
    """
    Old local team JSON saver.

    Used only when DATABASE_URL is missing.
    In Render production, we do NOT want this path.
    """
    try:
        normalized = _normalize_team(team)

        for pid, entry in normalized.items():
            # ✅ Keep old clean behavior:
            # If nickname is None/blank, don't store it.
            # If nickname is real, keep it.
            if entry.get("nickname") is None or entry.get("nickname") == "":
                entry.pop("nickname", None)

        with open(TEAM_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(normalized, file, indent=4, ensure_ascii=False)

        _team_bc(
            "FILE_SAVE_TEAM_OK",
            path=TEAM_FILE_PATH,
            count=len(normalized),
            nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
        )

    except Exception as e:
        _team_bc(
            "FILE_SAVE_TEAM_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        raise


def load_team() -> Dict[str, dict]:
    """
    Main team loader used by the app.

    Render production:
        DATABASE_URL present → load from Neon PostgreSQL.

    Local/dev/test:
        DATABASE_URL missing or TESTING=1 → load from data/team_data.json.
    """
    _team_bc("LOAD_TEAM_ENTER", storage=storage_debug())

    try:
        raw_data = load_json_document(
            key="team",
            fallback_loader=_load_team_from_file,
            expected_empty={},
        )

        team = _normalize_team(raw_data)

        _team_bc(
            "LOAD_TEAM_OK",
            count=len(team),
            storage=storage_debug(),
            nicknames={pid: entry.get("nickname") for pid, entry in team.items()},
        )

        return team

    except Exception as e:
        _team_bc(
            "LOAD_TEAM_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
            storage=storage_debug(),
        )
        raise


def save_team(team: Dict[str, Any]) -> None:
    """
    Main team saver used by the app.

    If DATABASE_URL exists:
        Saves to Neon.

    If DATABASE_URL is missing:
        Saves to local JSON fallback.

    This preserves old local behavior while making Render team data persistent.
    """
    _team_bc(
        "SAVE_TEAM_ENTER",
        incoming_type=type(team).__name__,
        incoming_len=len(team) if hasattr(team, "__len__") else None,
        storage=storage_debug(),
    )

    try:
        normalized = _normalize_team(team)

        for pid, entry in normalized.items():
            if entry.get("nickname") is None or entry.get("nickname") == "":
                entry.pop("nickname", None)

        _team_bc(
            "SAVE_TEAM_NORMALIZED",
            count=len(normalized),
            nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
            storage=storage_debug(),
        )

        saved_to_db = save_json_document("team", normalized)

        if saved_to_db:
            _team_bc(
                "SAVE_TEAM_DB_OK",
                count=len(normalized),
                nicknames={pid: entry.get("nickname") for pid, entry in normalized.items()},
                storage=storage_debug(),
            )

            # ✅ Immediate verification from Neon.
            verify_raw = load_json_document(
                key="team",
                fallback_loader=_load_team_from_file,
                expected_empty={},
            )
            verify_team = _normalize_team(verify_raw)

            _team_bc(
                "SAVE_TEAM_DB_VERIFY_OK",
                count=len(verify_team),
                verify_nicknames={
                    pid: entry.get("nickname")
                    for pid, entry in verify_team.items()
                },
                storage=storage_debug(),
            )

            return

        # ✅ Local fallback only when DB is disabled.
        _team_bc("SAVE_TEAM_FILE_FALLBACK_BEGIN", storage=storage_debug())
        _save_team_to_file(normalized)

    except Exception as e:
        _team_bc(
            "SAVE_TEAM_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
            storage=storage_debug(),
        )
        raise