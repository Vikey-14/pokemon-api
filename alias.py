from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app=FastAPI()

class Ability(BaseModel):
    name: str
    ptype: str
    power: int

class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name", min_length=2 )
    level:int
    abilities: List[Ability]

@app.post("/pokemon_ability", response_model= Pokemon)
def register_pokemon(pokemon: Pokemon):
    return pokemon