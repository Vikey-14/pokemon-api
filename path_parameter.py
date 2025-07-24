from fastapi import FastAPI,Path,status,HTTPException
from pydantic import BaseModel,Field
from typing import Optional,List,Dict
from file_handler import load_pokedex

app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias= "poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")


@app.get("/pokemon/{pokemon_id}")
def get_pokemon_info(pokemon_id:int=Path(...,ge=1,le=9999, title="Pokemon_ID", description= "Pokemon ID must be between 1-9999")):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Please enter valid pokemon id: {pokemon_id}")
    
    return{
        "message": "Pokemon ID matched!",
        "data": pokedex[pokemon_id]
    }
                     