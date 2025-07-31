from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel,Field
from typing import Dict,Optional,Union
from utils.file_handler import load_pokedex,save_pokedex


app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    ptype:str=Field(...,alias="Type")
    level:int=Field(...,ge=5,le=100)

class ResponsiveMessage(BaseModel):
    message:str
    data: Union[Pokemon,str]

@app.post("/pokemon", response_model= ResponsiveMessage,status_code=status.HTTP_201_CREATED, tags=["Admin Actions"])
def add_pokemon(pokemon:Pokemon):

    for existing in pokedex.values():
        if pokedex["poke_name"].lower()== pokemon.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail= f"Name Provided {pokemon.name} already exists in Pokedex"
            )
    
    new_id=max(pokedex.keys(), default=0)+1
    pokedex[new_id]= pokemon.dict(by_alias=True)
    save_pokedex(pokedex)

    return{
        "message": "Pokemon Data Added Successfully to the Pokedex.",
        "data": pokedex[new_id]
    }