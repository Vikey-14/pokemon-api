# 📦 dependencies/pokedex_provider.py

from utils.file_handler import load_pokedex
from config import settings
from custom_logger import error_logger


def _pdx_bc(event: str, **fields) -> None:
    try:
        parts = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
        print(f"[PDX_BC] {event}" + (f" {parts}" if parts else ""), flush=True)
    except Exception as e:
        print(f"[PDX_BC] {event} breadcrumb_error={type(e).__name__}:{e}", flush=True)

# 🔹 For /pokemon routes (string keys)
def get_pokedex_data():
    _pdx_bc("PDX_ENTER")

    try:
        _pdx_bc("PDX_BEFORE_LOAD_POKEDEX")
        pokedex = load_pokedex()

        _pdx_bc(
            "PDX_AFTER_LOAD_POKEDEX",
            pokedex_type=type(pokedex).__name__,
            pokedex_len=len(pokedex) if hasattr(pokedex, "__len__") else None,
        )

        if not isinstance(pokedex, dict):
            raise TypeError(f"Expected dict from load_pokedex(), got {type(pokedex).__name__}")

        _pdx_bc("PDX_RETURN_OK")
        return pokedex

    except Exception as e:
        _pdx_bc(
            "PDX_ERR",
            err_type=type(e).__name__,
            err=str(e),
        )
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
