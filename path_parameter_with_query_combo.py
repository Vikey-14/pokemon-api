from fastapi import Query,FastAPI,Path,HTTPException,status
from pydantic import BaseModel,Field
from typing import Optional,List,Dict,Union
from enum import Enum
from utils.file_handler import load_pokedex

app=FastAPI()

pokedex: Dict[int,dict]=load_pokedex()

class Region(str,Enum):
    kanto="Kanto"
    johto="Johto"
    hoenn="Hoenn"
    sinnoh="Sinnoh"
    unova="Unova"
    kalos="Kalos"
    alola="Alola"
    galar="Galar"
    paldea="Paldea"
    hisui="Hisui"

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name",title="Pokemon Name", description="Provides Pokemon Name", example="Charizard")
    level:int=Field(...,ge=5,le=100, title="Pokemon Level",desription="Provides Pokemon Level",example=25)
    ptype:str=Field(...,alias="Type", title="Pokemon Typing", description="Provides Pokemon Typing",example="Fire")
    region: Region = Field(..., title="Pokemon Region", description="Region to which this Pokémon belongs", example="Hoenn")


class ResponsiveMessage(BaseModel):
    message:str
    data:Union[Pokemon,str,List[Pokemon]]


@app.get(
    "/pokemon/{region_name}",
    response_model=ResponsiveMessage,
    tags=["Trainer View"],
    summary="Get Pokémon by Region with Optional Filters",
    description="Returns Pokémon from a given region. Supports optional filtering by level and type.",
    response_description="Filtered Pokémon list or 404 if none match"
)
def get_pokemon_by_region_filtered(
    region_name: Region = Path(..., title="Region", regex="^[A-Za-z]{3,20}$", description="One of the allowed regions",example="Hoenn"),
    level: int = Query(None, ge=5, le=100, description="Optional level filter",example=50),
    ptype: str = Query(None, regex="^[A-Za-z]{3,20}$", description="Optional Pokémon type filter",example="Fire")
):
    

    filtered = [
        p for p in pokedex.values()
        if p.get("region", "").lower() == region_name.value.lower()
        and (level is None or p.get("level") == level)
        and (ptype is None or p.get("Type", "").lower() == ptype.lower())
    ]

    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Pokémon found matching your criteria."
        )

    return {
        "message": f"{len(filtered)} Pokémon matched your filters.",
        "data": filtered
    }
