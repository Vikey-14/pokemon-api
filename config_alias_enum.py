from fastapi import FastAPI
from typing import List
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum

app = FastAPI()


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
    name:str
    mtype:List[MoveType]
    power: int

    @validator("power")
    def power_must_be_positive(cls,v):
        if v<1:
            raise ValueError("Power must be more than 1")
        return v
    

class Pokemon(BaseModel):
     name:str=Field(...,alias="poke_name", min_length=5)
     level:int=Field(...,ge=5, le=100)
     moves: List[Moves]

     @validator("name")
     def capitalize(cls,v):
         return v.capitalize()
     
     @root_validator
     def moves_level(cls,values):
         moves= values.get("moves")
         level= values.get("level")

         if not moves and len(moves)==0:
             raise ValueError("Moves should be atleast one.")
         
         avg_power=sum(move.power for move in moves)/ len(moves)
         if avg_power>level:
             raise ValueError("Power cannot be more than level.")
         return values

     class Config:
      use_enum_values=True
      anystr_strip_whitespace=True
      allow_population_by_field_name=True


@app.post("/config", response_model=Pokemon, response_model_by_alias=True)
def register_pokemon(pokemon:Pokemon):
    return pokemon