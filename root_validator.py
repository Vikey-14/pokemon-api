from fastapi import FastAPI
from pydantic import BaseModel,validator,Field, root_validator
from typing import List, Literal


app= FastAPI()

class Moves(BaseModel):
    name:str
    mtype: Literal["Fire", "Grass", "Electric", "Water", "Ghost"]
    power: int

    @validator("name")
    def strip_whitespace(cls, v):
        return v.strip()
    
    @validator("power")
    def power_must_be_positive(cls,v):
        if v<1:
            raise ValueError("Power must be greater than 1.")
        return v
    

class Pokemon(BaseModel):
    name: str= Field(..., alias="poke_name", min_length=5 )
    level: int= Field(...,ge=5, le=100)
    moves: List[Moves]

    @validator("name")
    def capitalize_name(cls,v):
        return v.capitalize()
    
    @root_validator
    def moves_level(cls,values):
        level= values.get("level")
        moves= values.get("moves")


        if not moves or len(moves)==0:
            raise ValueError("At least one move is required.")
        
        avg_power=sum(move.power for move in moves)/ len(moves)
        if avg_power> level:
            raise ValueError("Power cannot be more than level.")
        
        return values
    
@app.post("/root_eliminator", response_model=Pokemon)
def registration_pokemon(pokemon:Pokemon):   
   return pokemon     
        