from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app=FastAPI()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name",min_length=5)
    level:int=Field(...,ge=5,le=100)

    class Config:
        allow_population_by_field_name=True
        anystr_strip_whitespace=True


class Legendary(Pokemon):
    region_of_origin:str
    is_mythical:bool

@app.post("/inheritance", response_model=Legendary, response_model_by_alias=True)
def pokemon_registration(pokemon:Legendary):
    return pokemon
