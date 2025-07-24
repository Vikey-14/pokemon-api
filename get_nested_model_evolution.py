from fastapi import FastAPI
from pydantic import BaseModel,Field
from file_handler import load_pokedex
from typing import List,Dict,Optional,Union

app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()


class Evolution(BaseModel):
    current_stage:str
    next_evolution:Optional[str]=None
    evolution_level:Optional[int]=None


class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")
    evolution: Optional[Evolution]

class ResponsiveMessage(BaseModel):
    message: str
    data: Union[Pokemon, dict]

@app.get("/pokemon/evolution", response_model=ResponsiveMessage)
def get_all_with_evolution():
    return {
        "message": "All Pokémon with evolution info retrieved!",
          "data": list(pokedex.values())
      }