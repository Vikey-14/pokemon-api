from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from typing import List
from dependencies.pokedex_provider import get_pokedex_data
from utils.file_handler import save_pokedex, load_pokedex
from audit_logger import log_pokemon_addition
from custom_logger import info_logger
from auth.hybrid_auth import get_current_user, role_required
from utils.limiter_utils import limit_safe
from models.pokemon_model import Pokemon, PatchPokemon

router = APIRouter(prefix="/pokemon", tags=["Trainer View"])

# ✅ GET all Pokémon
@router.get("/", response_model=List[Pokemon], response_model_by_alias=False)
@limit_safe("10/minute")
async def get_all_pokemon(request: Request, current_user: str = Depends(get_current_user)):
    pokedex = load_pokedex()
    result = []

    for pid, data in pokedex.items():
        # 🧠 Ensure every Pokémon has a valid integer ID
        fixed_data = data.copy()
        fixed_data["id"] = int(pid)

        # 🧠 Ensure nickname key exists
        if "nickname" not in fixed_data:
            fixed_data["nickname"] = None

        # ✅ Validate and append
        pokemon = Pokemon.model_validate(fixed_data)
        result.append(pokemon)

    return result

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
    str_id = str(pokemon_id)
    print("🧠 PATCH lookup ID:", str_id)
    print("🧠 Current pokedex keys:", list(pokedex.keys()))

    if str_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon not found")

    pokemon = pokedex[str_id]

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
    str_id = str(pokemon_id)

    if str_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon not found")

    deleted = pokedex.pop(str_id)
    save_pokedex(pokedex)

    info_logger.info(f"🗑️ '{deleted['name']}' [ID {pokemon_id}] deleted by {current_user}")

    return {
        "Message": f"{deleted['name']} deleted by {current_user}!",
        "Data": {
            "id": pokemon_id,
            **deleted
        }
    }
