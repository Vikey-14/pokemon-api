from fastapi import FastAPI
from pydantic import BaseModel, PrivateAttr, Field
from typing import List

app = FastAPI()

class Ability(BaseModel):
    name: str
    ptype: str
    power: int

class Pokemon(BaseModel):
    name: str = Field(..., alias= "poke_name")
    level: int = Field(..., ge=5,le=100)
    abilities:List[Ability]

    _secret_technique:str= PrivateAttr(default="Volt Overload")

@app.post("/hidden_technique", response_model= Pokemon)
def hidden(pokemon:Pokemon):
    print("Hidden Move:", pokemon._secret_technique)
    return pokemon 

