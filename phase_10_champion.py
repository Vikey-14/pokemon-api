from fastapi import FastAPI, HTTPException, status, Path, Query
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Optional, List, Union
from utils.file_handler import load_pokedex

app = FastAPI()

pokedex: Dict[int, dict] = load_pokedex()

class Region(str, Enum):
    kanto = "Kanto"
    johto = "Johto"
    hoenn = "Hoenn"
    sinnoh = "Sinnoh"
    unova = "Unova"
    kalos = "Kalos"
    alola = "Alola"
    galar = "Galar"
    paldea = "Paldea"
    hisui = "Hisui"

class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name", title="Pokemon Name", description="Provides Pokemon Name", example="Charizard")
    level: int = Field(..., ge=5, le=100, title="Pokemon Level", description="Provides Pokemon Level", example=25)
    ptype: str = Field(..., alias="Type", title="Pokemon Typing", description="Provides Pokemon Typing", example="Fire")
    region: Region = Field(..., title="Pokemon Region", description="Region to which this Pokémon belongs", example="Hoenn")

class ResponsiveMessage(BaseModel):
    message: str
    data: Union[Pokemon, str, List[Pokemon]]

@app.get(
    "/trainerbox/level/{min_level}/{max_level}",
    response_model=ResponsiveMessage,
    tags=["Trainer View"],
    summary="Get pokemon by min Level and max level provided where its typing is optional.",
    description="Returns Pokemon by Min and Max Level. Supports Optional filtering by the pokemon's typing.",
    response_description="Filtered Pokemon List or 404 if none match."
)
def get_pokemon_by_pokemon_level_filtered(
    min_level: int = Path(..., ge=5, le=100, title="Minimum Pokemon Level", description="level filter", example=5),
    max_level: int = Path(..., ge=5, le=100, title="Maximum Pokemon Level", description="level filter", example=100),
    ptype: str = Query(None, regex="^[A-Za-z]{3,20}$", description="Optional Pokémon type filter", example="Fire")
):
    if min_level > max_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum level cannot be greater than maximum level."
        )

    filtered = [
        p for p in pokedex.values()
        if min_level <= p.get("level", 0) <= max_level
        and (ptype is None or p.get("Type", "").lower() == ptype.lower())
    ]

    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pokemon found in the level range provided."
        )

    return {
        "message": f"{len(filtered)} Pokemon Information fetched from the details provided.",
        "data": filtered
    }
