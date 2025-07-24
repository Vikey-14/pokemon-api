from fastapi import FastAPI, Path, status, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, List, Union
from file_handler import load_pokedex

app = FastAPI()

pokedex: Dict[int, dict] = load_pokedex()

# --- Model for single Pokemon ---
class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name")
    level: int = Field(..., ge=5, le=100)
    ptype: str = Field(..., alias="Type")
    region: str

# --- Response wrapper ---
class ResponsiveMessage(BaseModel):
    message: str
    data: Union[Pokemon, List[Pokemon], str]

# --- Enum for valid regions ---
class Region(str, Enum):
    kanto = "Kanto"
    johto = "Johto"
    hoenn = "Hoenn"
    sinnoh = "Sinnoh"

# --- Route with Swagger enhancements ---
@app.get(
    "/region/{region_name}",
    response_model=ResponsiveMessage,
    tags=["Trainer View"],
    summary="Get Pokémon by Region",
    description="Returns all Pokémon found in the specified region. Only allows predefined regions.",
    response_description="List of Pokémon from that region or an error message."
)
def get_pokemon_by_region(
    region_name: Region = Path(..., title="Region Name", description="Region must be one of: Kanto, Johto, Hoenn, Sinnoh")
):
    matched = [
        p for p in pokedex.values()
        if p.get("region", "").lower() == region_name.value.lower()
    ]

    if not matched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Pokémon found matching your criteria: {region_name}"
        )

    return {
        "message": f"{len(matched)} Pokémon found from {region_name} region.",
        "data": matched
    }
