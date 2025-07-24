from fastapi import FastAPI
from pydantic import BaseModel,Field,validator,root_validator
from typing import List,Union
from enum import Enum
from datetime import datetime

app=FastAPI()

class BaseStats(BaseModel):
    id:int
    created_at:datetime =Field(default_factory=datetime.utcnow)

class MoveType(str, Enum):
    fire="Fire"
    water="Water"
    grass="Grass"
    electric="Electric"
    rock="Rock"
    bug="Bug"
    ground="Ground"
    flying="Flying"
    ice="Ice"
    steel="Steel"
    dark="Dark"
    ghost="Ghost"
    psychic="Psychic"
    fairy="Fairy"
    dragon="Dragon"
    normal="Normal"
    fighting="Fighting"
    poison="Poison"

class Moves(BaseModel):
    name:str=Field(...,alias="move_name", description="Name of Pokemon Move.", example="Earthquake")
    mtype:List[MoveType] =Field(..., example=["Ground"])
    power:int=Field(...,ge=1, description="Power must be atleast equal to one.", example=100)

    @validator("name")
    def move_name_capitalize(cls,v):
        return v.capitalize()
    
    @validator("power")
    def power_must_be_positive(cls,v):
        if v<1:
            raise ValueError("Power should be greater than 1.")
        return v
    
    class Config:
        allow_population_by_field_name=True
        use_enum_values=True
        anystr_strip_whitespace=True

class Pokemon(BaseStats):
    name:str=Field(...,alias="poke_name",min_length=5, description="Name of Pokemon", example="Garchomp")
    level:int=Field(...,ge=1,le=100, example=85)
    types: List[MoveType] =Field(..., example=["Ground"])
    moves: List[Moves]
    
    
    @validator("name")
    def poke_name_capitalize(cls,v):
        return v.capitalize()
    
    @validator("types")
    def types(clas,v):
        if len(v)>2:
            raise ValueError("Pokemon typing cannot be more than 2.")
        return v
     
    @root_validator
    def moves_level(cls,values):
        moves=values.get("moves")
        level=values.get("level")

        if not moves or len(moves)==0:
            raise ValueError("Moves should be atleast 1.")
        
        avg_power=sum(move.power for move in moves)/ len(moves)
        if avg_power> level:
            raise ValueError("Power cannot be more than level of Pokemon")
        return values
  
    class Config:
     allow_population_by_field_name=True
     use_enum_values=True
     anystr_strip_whitespace=True   
   

class Legendary(Pokemon):
    region_of_origin:str=Field(...,min_length=5, example="Hoenn")
    is_mythical:bool 


@app.post("/pokedex_registry",response_model= Union[Pokemon,Legendary], response_model_by_alias=True)
def pokedex(pokemon: Union[Pokemon,Legendary]):
    return pokemon

