from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import List, Dict, Optional
from auth.security import verify_token
from utils.team_handler import load_team, save_team
from dependencies.pokedex_provider import get_team_pokedex_data
from pydantic import BaseModel, Field
from custom_logger import info_logger, error_logger
from utils.limiter_utils import limit_safe 

router = APIRouter(prefix="/team", tags=["Gym Battle Team"])


# ✅ Desk 1 – View current team
@router.get("/", response_model=List[dict])
@limit_safe("5/minute")  
async def get_team(request: Request, current_user: str = Depends(verify_token)):
    try:
        team = load_team()
        return list(team.values())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Desk 2 – Add Pokémon to team
@router.post("/{pokemon_id}", status_code=status.HTTP_201_CREATED)
@limit_safe("6/minute") 
async def add_to_team(
    request: Request,
    pokemon_id: int,
    pokedex=Depends(get_team_pokedex_data),
    current_user: str = Depends(verify_token)
):
    try:
        team = load_team()

        if pokemon_id not in pokedex:
            raise HTTPException(status_code=404, detail=f"Invalid ID {pokemon_id}! Pokémon not found in Pokédex.")

        if str(pokemon_id) in team:
            raise HTTPException(status_code=409, detail=f"Invalid ID {pokemon_id}! Pokémon already in the team.")

        if len(team) >= 6:
            raise HTTPException(status_code=400, detail="Team Full! Maximum six Pokémon allowed.")

        team[str(pokemon_id)] = pokedex[pokemon_id]
        save_team(team)

        return {"Message": "Pokémon added to your team.", "Team": list(team.values())}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Desk 3 – Remove Pokémon
@router.delete("/{pokemon_id}", status_code=status.HTTP_200_OK)
@limit_safe("6/minute")  
async def remove_from_team(
    request: Request,
    pokemon_id: int,
    current_user: str = Depends(verify_token)
):
    try:
        team = load_team()
        pid = str(pokemon_id)

        if pid not in team:
            error_logger.error(f"❌ Remove failed by {current_user} – ID {pid} not in team")
            raise HTTPException(status_code=404, detail=f"Cannot remove! Pokémon ID {pid} is not in your team.")

        removed = team.pop(pid)
        save_team(team)

        info_logger.info(f"❌ {removed.get('poke_name') or removed.get('name')} [ID {pid}] removed from team by {current_user}")
        return {"Message": f"Pokémon {removed.get('poke_name') or removed.get('name')} removed from your team.", "Team": list(team.values())}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Desk 4 – Average level
@router.get("/average-level", status_code=status.HTTP_200_OK)
@limit_safe("10/minute") 
async def average_team_level(request: Request, current_user: str = Depends(verify_token)):
    try:
        team = load_team()

        if not team:
            error_logger.error(f"❌ Average level check failed by {current_user} – Team is empty")
            raise HTTPException(status_code=400, detail="Team is empty! Add Pokémon to get average level.")

        total_level = sum(int(p["level"]) for p in team.values())
        average = round(total_level / len(team), 2)

        return {
            "Message": "Trainer Strength Evaluated!",
            "Average Level": average,
            "Team Size": len(team)
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Desk 5 – PATCH updates
class UpgradePokemon(BaseModel):
    level: Optional[int] = Field(None, ge=5, le=100)
    nickname: Optional[str] = Field(None, min_length=5, max_length=15)

@router.patch("/{pokemon_id}", status_code=status.HTTP_200_OK)
@limit_safe("5/minute")  
async def upgrade_pokemon(
    request: Request,
    pokemon_id: int,
    updates: UpgradePokemon,
    current_user: str = Depends(verify_token)
):
    try:
        team = load_team()
        pid = str(pokemon_id)

        if pid not in team:
            error_logger.error(f"❌ Upgrade failed by {current_user} – ID {pid} not in team")
            raise HTTPException(status_code=404, detail=f"Pokémon ID {pid} is not in your team.")

        pokemon = team[pid]
        changes = []

        if updates.level is not None:
            pokemon["level"] = int(updates.level)
            changes.append(f"Level {updates.level}")
        if updates.nickname is not None:
            pokemon["nickname"] = updates.nickname
            changes.append(f"Nickname '{updates.nickname}'")

        team[pid] = pokemon
        save_team(team)

        change_str = ", ".join(changes) if changes else "No changes"
        info_logger.info(f"🔧 {pokemon.get('poke_name') or pokemon.get('name')} [ID {pid}] upgraded by {current_user}: {change_str}")

        return {"Message": f"Pokémon ID {pid} updated!", "Updated Info": pokemon}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
