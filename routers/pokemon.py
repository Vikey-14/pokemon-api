from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from typing import List, Optional
from pydantic import BaseModel
from models.pokemon import Pokemon
from dependencies.pokedex_provider import get_pokedex_data
from file_handler import save_pokedex
from audit_logger import log_pokemon_addition
from custom_logger import info_logger, error_logger  # ✅ Both loggers
from auth.hybrid_auth import get_current_user, role_required  

router = APIRouter(
    prefix="/pokemon",
    tags=["Trainer View"]
)

# ✅ GET all Pokémon (🔓 Accessible by any logged-in user)
@router.get("/", response_model=List[Pokemon])
def get_all_pokemon(
    current_user: str = Depends(get_current_user),
    pokedex=Depends(get_pokedex_data)
):
    return list(pokedex.values())

# ✅ POST: Add a new Pokémon (🔒 Only Admin can add to Pokédex)
@router.post("/", status_code=status.HTTP_200_OK)
def add_pokemon(
    pokemon: Pokemon,
    background_tasks: BackgroundTasks,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(role_required("admin"))
):
    new_id = max(pokedex.keys(), default=0) + 1

    pokedex[new_id] = {
        "poke_name": pokemon.name,
        "level": pokemon.level,
        "Type": pokemon.ptype
    }

    save_pokedex(pokedex)

    # ✅ Background audit log
    background_tasks.add_task(log_pokemon_addition, current_user, pokemon.name, new_id)

    # ✅ Real-time log
    info_logger.info(f"✅ '{pokemon.name}' [ID {new_id}] added by {current_user}")

    return {
        "Message": f"{pokemon.name} added by {current_user}!",
        "Data": pokedex[new_id]
    }

# ✅ PATCH: Update Pokémon's level/type (🔒 Admin-only)
class PatchPokemon(BaseModel):
    level: Optional[int] = None
    ptype: Optional[str] = None

@router.patch("/{pokemon_id}", status_code=200)
def update_pokemon(
    pokemon_id: int,
    updated_data: PatchPokemon,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(role_required("admin"))
):
    if pokemon_id not in pokedex:
        error_logger.error(f"❌ Update failed by {current_user} – ID {pokemon_id} not found")
        raise HTTPException(status_code=404, detail="Pokemon not found")

    pokemon = pokedex[pokemon_id]

    if updated_data.level is not None:
        pokemon["level"] = updated_data.level
    if updated_data.ptype is not None:
        pokemon["Type"] = updated_data.ptype

    save_pokedex(pokedex)

    info_logger.info(f"✏️ '{pokemon['poke_name']}' [ID {pokemon_id}] updated by {current_user}")

    return {
        "Message": f"{pokemon['poke_name']} updated by {current_user}!",
        "Data": pokemon
    }

# ✅ DELETE: Remove Pokémon from Pokédex (🔒 Admin-only)
@router.delete("/{pokemon_id}", status_code=200)
def delete_pokemon(
    pokemon_id: int,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(role_required("admin"))
):
    if pokemon_id not in pokedex:
        error_logger.error(f"❌ Deletion failed by {current_user} - ID {pokemon_id} not found")
        raise HTTPException(status_code=404, detail="Pokemon not found")

    deleted = pokedex.pop(pokemon_id)
    save_pokedex(pokedex)

    info_logger.info(f"🗑️ '{deleted['poke_name']}' [ID {pokemon_id}] deleted by {current_user}")

    return {
        "Message": f"{deleted['poke_name']} deleted by {current_user}!",
        "Data": deleted
    }
