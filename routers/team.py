from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Optional
from auth.security import verify_token  
from dependencies.pokedex_provider import get_pokedex_data
from pydantic import BaseModel, Field
from custom_logger import info_logger, error_logger  # ✅ Log both success and errors

router = APIRouter(prefix="/team", tags=["Gym Battle Team"])

# 👥 In-memory team storage
team: Dict[int, dict] = {}

# ✅ Desk 1 – View current team
@router.get("/", response_model=List[dict])
def get_team(current_user: str = Depends(verify_token)):
    return list(team.values())

# ✅ Desk 2 – Add Pokémon to team
@router.post("/{pokemon_id}", status_code=status.HTTP_201_CREATED)
def add_to_team(
    pokemon_id: int,
    pokedex=Depends(get_pokedex_data),
    current_user: str = Depends(verify_token)
):
    if pokemon_id not in pokedex:
        error_logger.error(f"❌ Add failed by {current_user} – ID {pokemon_id} not in Pokédex")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid ID {pokemon_id}! Pokémon not found in Pokédex."
        )
    if pokemon_id in team:
        error_logger.error(f"❌ Add failed by {current_user} – ID {pokemon_id} already in team")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid ID {pokemon_id}! Pokémon already in the team."
        )
    if len(team) >= 6:
        error_logger.error(f"❌ Add failed by {current_user} – Team full (6 Pokémon)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team Full! Maximum six Pokémon allowed."
        )
    
    pokemon = pokedex[pokemon_id]
    team[pokemon_id] = pokemon

    info_logger.info(f"🔥 {pokemon['poke_name']} [ID {pokemon_id}] added to team by {current_user}")
    return {
        "Message": "Pokémon added to your team.",
        "Team": list(team.values())
    }

# ✅ Desk 3 – Remove Pokémon from team
@router.delete("/{pokemon_id}", status_code=status.HTTP_200_OK)
def remove_from_team(
    pokemon_id: int,
    current_user: str = Depends(verify_token)
):
    if pokemon_id not in team:
        error_logger.error(f"❌ Remove failed by {current_user} – ID {pokemon_id} not in team")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot remove! Pokémon ID {pokemon_id} is not in your team."
        )
    removed = team.pop(pokemon_id)
    info_logger.info(f"❌ {removed['poke_name']} [ID {pokemon_id}] removed from team by {current_user}")
    return {
        "Message": f"Pokémon {removed['poke_name']} removed from your team.",
        "Team": list(team.values())
    }

# ✅ Desk 4 – Get average level
@router.get("/average-level", status_code=status.HTTP_200_OK)
def average_team_level(current_user: str = Depends(verify_token)):
    if not team:
        error_logger.error(f"❌ Average level check failed by {current_user} – Team is empty")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is empty! Add Pokémon to get average level."
        )
    total_level = sum(p["level"] for p in team.values())
    average = round(total_level / len(team), 2)
    return {
        "Message": "Trainer Strength Evaluated!",
        "Average Level": average,
        "Team Size": len(team)
    }

# ✅ Desk 5 – PATCH: Level up or rename Pokémon
class UpgradePokemon(BaseModel):
    level: Optional[int] = Field(None, ge=5, le=100, description="Enter the level of the Pokémon.")
    nickname: Optional[str] = Field(None, min_length=5, max_length=15, description="Enter the nickname you'd like to give.")

@router.patch("/{pokemon_id}", status_code=status.HTTP_200_OK)
def upgrade_pokemon(
    pokemon_id: int,
    updates: UpgradePokemon,
    current_user: str = Depends(verify_token)
):
    if pokemon_id not in team:
        error_logger.error(f"❌ Upgrade failed by {current_user} – ID {pokemon_id} not in team")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokémon ID {pokemon_id} is not in your team."
        )

    pokemon = team[pokemon_id]

    # Apply updates
    changes = []
    if updates.level is not None:
        pokemon["level"] = updates.level
        changes.append(f"Level {updates.level}")
    if updates.nickname is not None:
        pokemon["nickname"] = updates.nickname
        changes.append(f"Nickname '{updates.nickname}'")

    change_str = ", ".join(changes) if changes else "No changes"
    info_logger.info(f"🔧 {pokemon['poke_name']} [ID {pokemon_id}] upgraded by {current_user}: {change_str}")

    return {
        "Message": f"Pokémon ID {pokemon_id} updated!",
        "Updated Info": pokemon
    }
