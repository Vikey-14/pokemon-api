from fastapi import FastAPI
from  file_handler import load_pokedex
from pydantic import BaseModel, Field
from typing import List,Dict 


app=FastAPI()

pokedex: Dict[int, dict]= load_pokedex()


class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int
    ptype:str=Field(...,alias="Type")


@app.get("/pokemon", response_model=List[Pokemon])
def get_all_pokemon():
    return list(pokedex.values())


@app.get("/pokemon/type/{ptype}", response_model=List[Pokemon])
def get_pokemon_by_type(ptype: str):
    filtered= ( p for p in pokedex.values()
              if p["Type"].lower() == ptype.lower()
      )
    return filtered