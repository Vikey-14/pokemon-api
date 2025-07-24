from fastapi import FastAPI, Query, status
from typing import List, Dict
from pydantic import BaseModel, Field
from file_handler import load_pokedex

app = FastAPI()

pokedex: Dict[int, dict] = load_pokedex()

class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name", example="Charizard")
    ptype: str = Field(..., alias="Type", example="Fire/Flying")
    level: int = Field(..., ge=5, le=100, example=85)

@app.get(
    "/pokemon/by-level",
    response_model=List[Pokemon],
    summary="Filter Pokémon by Level Range",
    description="Returns all Pokémon in the Pokédex with levels between min_level and max_level (inclusive).",
    tags=["Trainer View"],
    response_description="List of Pokémon matching the level criteria"
)
def filter_by_level(
    min_level: int = Query(5, ge=5, le=100, description="Minimum level (5–100)"),
    max_level: int = Query(100, ge=5, le=100, description="Maximum level (5–100)")
):
    filtered = [
        p for p in pokedex.values()
        if min_level <= p["level"] <= max_level
    ]
    return filtered
