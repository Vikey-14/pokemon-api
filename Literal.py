from fastapi import FastAPI
from typing import Literal, List
from pydantic import BaseModel, Field

app= FastAPI()

class Moves(BaseModel):
    name: str
    mtype:Literal["Fire","Water","Electric"]
    power: int

class Pokemon(BaseModel):
    name: str= Field(..., alias="poke_name", min_length=5)
    level: int= Field(..., ge=5, le=100)
    moves: List[Moves]

@app.post("/literal", response_model= Pokemon)
def register_pokemon(pokemon: Pokemon):
    return pokemon
