from fastapi import Query, FastAPI
from typing import Optional,Dict,List
from file_handler import load_pokedex
from pydantic import BaseModel,Field


app=FastAPI()

pokedex:Dict[int,dict]= load_pokedex()


class Pokemon(BaseModel):
      name: str = Field(..., alias="poke_name", example="Charizard")
      ptype: str = Field(..., alias="Type", example="Fire/Flying")
      level: int = Field(..., ge=5, le=100, example=85)

@app.get(
    "/pokemon/filtered",
    response_model=List[Pokemon],
    summary="Advanced Filtered Pokémon View",
    description="""
    Allows sorting by name or level, and basic pagination using limit and offset.
    """,
    tags=["Trainer View"],
    response_description="Sorted and paginated list of Pokémon"
)
def get_filtered_pokemon(
    sort_by: Optional[str] = Query("level", pattern="^(name|level)$", description="Field to sort by: 'name' or 'level'"),
    order: Optional[str] = Query("asc", pattern="^(asc|desc)$", description="Order of sorting: 'asc' or 'desc'"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Number of Pokémon to return"),
    offset: Optional[int] = Query(0, ge=0, description="Number of Pokémon to skip")
):
    pokemon_list = list(pokedex.values())

    # Sorting
    reverse_order = True if order == "desc" else False
    pokemon_list.sort(key=lambda p: p[sort_by], reverse=reverse_order)

    # Pagination
    paginated = pokemon_list[offset:offset+limit]
    return paginated
