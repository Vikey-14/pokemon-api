from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import Union,Dict
from file_handler import load_pokedex

app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class ResponsiveMessage(BaseModel):
    message: str
    data:Union[Pokemon,str]


@app.get("/pokemon/{pokemon_id}", response_model=ResponsiveMessage)
def get_pokmeon_id(pokemon_id: int):
    if pokemon_id not in pokedex:
        return{
                "message": "Pokemon not found!",
                "data": "No data available for the requested ID."

        }
    return{
        "message": "Pokemon found!",
        "data": pokedex[pokemon_id]
    }