from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import List,Optional,Dict
from file_handler import load_pokedex


app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Evolution(BaseModel):
    next_stage:str
    evolution_level:Optional[int]

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    evolution:Optional[List[Evolution]]

@app.get("/pokemon/branching/", response_model=List[Pokemon])
def eevee_evolutions():
    return list(pokedex.values())