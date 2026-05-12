from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from typing import List, Any
from dependencies.pokedex_provider import get_pokedex_data
from utils.file_handler import save_pokedex, load_pokedex
from audit_logger import log_pokemon_addition
from custom_logger import info_logger
from auth.hybrid_auth import get_current_user, role_required
from utils.limiter_utils import limit_safe
from models.pokemon_model import Pokemon, PatchPokemon


def _poke_bc(event: str, **fields) -> None:
    try:
        parts = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
        print(f"[POKE_BC] {event}" + (f" {parts}" if parts else ""), flush=True)
    except Exception as e:
        print(f"[POKE_BC] {event} breadcrumb_error={type(e).__name__}:{e}", flush=True)


router = APIRouter(prefix="/pokemon", tags=["Trainer View"])


# ✅ GET all Pokémon
@router.get("/", response_model=List[Pokemon], response_model_by_alias=False)
@limit_safe("10/minute")
async def get_all_pokemon(
    request: Request,
    pokedex=Depends(get_pokedex_data),
    current_user: dict = Depends(get_current_user),
):
    _poke_bc("POKE_LIST_ENTER", user=current_user.get("username"), role=current_user.get("role"))

    result = []

    try:
        _poke_bc(
            "POKE_LIST_SOURCE_READY",
            pokedex_type=type(pokedex).__name__,
            pokedex_len=len(pokedex) if hasattr(pokedex, "__len__") else None,
        )

        for pid, data in pokedex.items():
            try:
                _poke_bc("POKE_LIST_ITEM_BEGIN", pid=pid, raw=data)

                if not isinstance(data, dict):
                    raise TypeError(f"Entry for pid {pid} is not a dict")

                fixed_data = data.copy()

                # Always normalize id
                fixed_data["id"] = int(fixed_data.get("id", pid))

                # Support both old and new naming styles
                if "name" not in fixed_data and "poke_name" in fixed_data:
                    fixed_data["name"] = fixed_data.get("poke_name")
                if "poke_name" not in fixed_data and "name" in fixed_data:
                    fixed_data["poke_name"] = fixed_data.get("name")

                # Normalize nickname
                fixed_data["nickname"] = fixed_data.get("nickname") or None

                # Normalize level if it came as text
                if fixed_data.get("level") is not None:
                    fixed_data["level"] = int(fixed_data["level"])

                pokemon = Pokemon.model_validate(fixed_data)
                result.append(pokemon)

                _poke_bc("POKE_LIST_ITEM_OK", pid=pid, normalized=fixed_data)

            except Exception as e:
                _poke_bc(
                    "POKE_LIST_ITEM_ERR",
                    pid=pid,
                    raw=data,
                    err_type=type(e).__name__,
                    err=str(e),
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Pokémon list failed at id {pid}: {type(e).__name__}: {e}",
                )

        _poke_bc("POKE_LIST_OK", count=len(result))
        return result

    except HTTPException:
        raise
    except Exception as e:
        _poke_bc("POKE_LIST_ERR", err_type=type(e).__name__, err=str(e))
        raise HTTPException(status_code=500, detail="Pokémon list crash")
    


@router.get("/{pokemon_id}", response_model=Pokemon, response_model_by_alias=False)
async def get_pokemon_by_id(
    request: Request,
    pokemon_id: int,
    pokedex=Depends(get_pokedex_data),
    current_user: dict = Depends(get_current_user),
):
    _poke_bc(
        "POKE_GET_BY_ID_ENTER",
        pokemon_id=pokemon_id,
        user=current_user.get("username"),
        role=current_user.get("role"),
    )

    try:
        lookup_key = None
        if pokemon_id in pokedex:
            lookup_key = pokemon_id
        elif str(pokemon_id) in pokedex:
            lookup_key = str(pokemon_id)

        _poke_bc(
            "POKE_GET_BY_ID_LOOKUP",
            pokemon_id=pokemon_id,
            pokedex_keys=list(pokedex.keys())[:20] if hasattr(pokedex, "keys") else None,
            resolved_key=lookup_key,
        )

        if lookup_key is None:
            raise HTTPException(status_code=404, detail="Pokemon not found")

        data = pokedex[lookup_key]
        if not isinstance(data, dict):
            raise TypeError(f"Entry for pokemon_id {pokemon_id} is not a dict")

        fixed_data = data.copy()
        fixed_data["id"] = int(fixed_data.get("id", pokemon_id))

        if "name" not in fixed_data and "poke_name" in fixed_data:
            fixed_data["name"] = fixed_data.get("poke_name")
        if "poke_name" not in fixed_data and "name" in fixed_data:
            fixed_data["poke_name"] = fixed_data.get("name")

        fixed_data["nickname"] = fixed_data.get("nickname") or None

        if fixed_data.get("level") is not None:
            fixed_data["level"] = int(fixed_data["level"])

        pokemon = Pokemon.model_validate(fixed_data)

        _poke_bc("POKE_GET_BY_ID_OK", pokemon_id=pokemon_id, normalized=fixed_data)
        return pokemon

    except HTTPException:
        raise
    except Exception as e:
        _poke_bc(
            "POKE_GET_BY_ID_ERR",
            pokemon_id=pokemon_id,
            err_type=type(e).__name__,
            err=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Pokemon fetch failed: {type(e).__name__}: {e}")
    

# ✅ ADD new Pokémon
@router.post("/", status_code=status.HTTP_201_CREATED)
@limit_safe("3/minute")
async def add_pokemon(
    request: Request,
    pokemon: Pokemon,
    background_tasks: BackgroundTasks,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(role_required("admin"))
):
    new_id = max([int(k) for k in pokedex.keys()], default=0) + 1
    model_dump = pokemon.model_dump()

    # 🧹 Remove None nicknames for cleanliness
    if model_dump.get("nickname") is None:
        model_dump.pop("nickname", None)

    model_dump["id"] = new_id
    pokedex[str(new_id)] = model_dump
    print("🐛 Final Pokedex (before saving):", pokedex)

    save_pokedex(pokedex)
    background_tasks.add_task(log_pokemon_addition, current_user, pokemon.name, new_id)

    return {
        "Message": f"{pokemon.name} added by {current_user}!",
        "Data": {
            "id": new_id,
            **model_dump,
            "nickname": model_dump.get("nickname", None)
        }
    }

# ✅ PATCH Pokémon
@router.patch("/{pokemon_id}", status_code=status.HTTP_200_OK)
@limit_safe("5/minute")
async def update_pokemon(
    request: Request,
    pokemon_id: int,
    updated_data: PatchPokemon,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(role_required("admin"))
):
    lookup_key = None
    if pokemon_id in pokedex:
        lookup_key = pokemon_id
    elif str(pokemon_id) in pokedex:
        lookup_key = str(pokemon_id)

    print("🧠 PATCH lookup ID:", pokemon_id)
    print("🧠 Current pokedex keys:", list(pokedex.keys()))
    print("🧠 PATCH resolved key:", lookup_key)

    if lookup_key is None:
        raise HTTPException(status_code=404, detail="Pokemon not found")

    pokemon = pokedex[lookup_key]

    # 🛠️ Apply partial updates
    if updated_data.level is not None:
        pokemon["level"] = updated_data.level
    if updated_data.ptype is not None:
        pokemon["ptype"] = updated_data.ptype
    if updated_data.nickname is not None:
        pokemon["nickname"] = updated_data.nickname

    save_pokedex(pokedex)
    info_logger.info(f"✏️ '{pokemon['name']}' [ID {pokemon_id}] updated by {current_user}")

    return {
        "Message": f"{pokemon['name']} updated by {current_user}!",
        "Data": {
            "id": pokemon_id,
            **pokemon
        }
    }

# ✅ DELETE Pokémon
@router.delete("/{pokemon_id}", status_code=status.HTTP_200_OK)
@limit_safe("5/minute")
async def delete_pokemon(
    request: Request,
    pokemon_id: int,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(role_required("admin"))
):
    lookup_key = None
    if pokemon_id in pokedex:
        lookup_key = pokemon_id
    elif str(pokemon_id) in pokedex:
        lookup_key = str(pokemon_id)

    print("🧠 DELETE lookup ID:", pokemon_id)
    print("🧠 Current pokedex keys:", list(pokedex.keys()))
    print("🧠 DELETE resolved key:", lookup_key)

    if lookup_key is None:
        raise HTTPException(status_code=404, detail="Pokemon not found")

    deleted = pokedex.pop(lookup_key)
    save_pokedex(pokedex)

    info_logger.info(f"🗑️ '{deleted['name']}' [ID {pokemon_id}] deleted by {current_user}")

    return {
        "Message": f"{deleted['name']} deleted by {current_user}!",
        "Data": {
            "id": pokemon_id,
            **deleted
        }
    }
