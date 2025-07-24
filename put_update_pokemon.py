from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from typing import Dict


app=FastAPI()

pokedex: Dict[int,dict]= {

    1: {"Name": "Bulbasaur", "Type": "Grass/Poison", "Level": 5}
}


class Pokemon(BaseModel):
    Name:str
    PType:str= Field(...,alias="Type")
    Level:int

@app.put("/pokemon/{pokemon_id}")
def update_pokemon(pokemon_id:int, updated_pokemon: Pokemon):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    
    pokedex[pokemon_id]= updated_pokemon.dict(by_alias=True)
    return{"Message": "Pokemon Updated!", "Data": pokedex[pokemon_id]}