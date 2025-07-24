from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional

app=FastAPI()

pokedex: Dict[int,dict]={
    1:{"Name": "Bulbasaur", "Type": "Grass/Poison", "Level": 5}
}

class Pokemon(BaseModel):
    Name: Optional[str]= None
    Type: Optional[str]=None
    Level: Optional[int]= None


@app.patch("/patch/{pokemon_id}")
def update_pokemon(pokemon_id:int, patched_pokemon: Pokemon):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon not found.")
    
    for field,value in patched_pokemon.dict(exclude_unset=True).items():
        pokedex[pokemon_id][field]=value

    return{"Message": "Patch Updated!", "Data": pokedex[pokemon_id]}


