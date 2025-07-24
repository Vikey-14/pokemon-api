from fastapi import FastAPI
from typing import List, Literal
from pydantic import BaseModel, Field, validator


app= FastAPI()

class Moves(BaseModel):
    name: str
    mtype: Literal["Fire", "Water", "Electric", "Grass", "Ghost"]
    power: int

    @validator("name")
    def strip_whitespace(cls,v):
        return v.strip()
    
    @validator("power")
    def power_must_be_positive(cls,v):
        if v<1:
            raise ValueError("Power must be atleast 1.")
        return v            
    

class Pokemon(BaseModel):
    name: str= Field(..., alias="poke_name", min_length=5)
    level: int= Field(...,ge=5, le=100)
    moves: List[Moves]

    @validator("name")
    def capitalize_name(cls,v):
        return v.capitalize()
    
@app.post("/validator", response_model=Pokemon)
def pokemon_registration(pokemon: Pokemon):
    return pokemon
