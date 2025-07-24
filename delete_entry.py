from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Dict


app=FastAPI()


pokedex:Dict[int, dict]={

    1: {"Name": "Bulbasaur", "Type": "Grass/Poison", "Level":10},
    2: {"Name": "Charmander", "Type": "Fire", "Level": 10 }
}

@app.delete("/delete/{pokemon_id}")
def deleted_pokemon(pokemon_id:int):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon Not Found.")
    
    deleted_pokemon=pokedex.pop(pokemon_id)

    return{
        "Message": f"Pokemon with ID {pokemon_id} has been deleted.",
        "Deleted Pokemon": deleted_pokemon,
        "Remaining Pokemon": pokedex,
    }

