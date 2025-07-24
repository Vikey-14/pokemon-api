from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

app=FastAPI()


class MoveType(str, Enum):
    fire ="Fire"
    water= "Water"
    electric="Electric"
    grass="Grass"
    psychic="Psychic"
    ghost="Ghost"
    dark="Dark"
    poison="Poison"
    bug="Bug"
    dragon="Dragon"
    fairy="Fairy"
    fighting="Fighting"
    ice="Ice"
    normal="Normal"
    steel="Steel"
    ground="Ground"
    rock="Rock"
    flying="Flying"

class Moves(BaseModel):
    name: str 
    mtype: MoveType
    power: int


class Pokemon(BaseModel):
    name: str= Field(..., min_length=2, alias="poke_name")
    level: int= Field(..., ge=5, le=100)
    moves: List[Moves]

@app.post("/abilities", response_model= Pokemon)
def enum_ability(pokemon : Pokemon):
    return pokemon
