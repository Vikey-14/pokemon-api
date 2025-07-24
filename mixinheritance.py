from fastapi import FastAPI 
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


app=FastAPI()

class BaseStats(BaseModel):
    id:int
    created_at: datetime=Field(default_factory=datetime.utcnow)

class Pokemon(BaseStats):
    name:str=Field(...,alias="poke_name", min_length=5)
    level:int= Field(...,ge=5,le=100)
    types:List[str]


class Trainer(BaseStats):
    name:str
    badges:int

@app.post("/pokemon", response_model=Pokemon)
def create_Pokemon(pokemon: Pokemon):
    return pokemon

@app.post("/trainer", response_model=Trainer)
def create_trainer(trainer: Trainer):
    return trainer
