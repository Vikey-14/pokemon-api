from fastapi import FastAPI
from typing import Dict,Optional,Union
from pydantic import BaseModel,Field
from utils.file_handler import save_pokedex, load_pokedex

app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class ResponsiveMessage(BaseModel):
    message: str
    data: Dict[str, Union[Pokemon, int, str]]

@app.delete("/pokemon/delete/{pokemon_id}",response_model= ResponsiveMessage)
def delete_pokemon(pokemon_id:int, delete_pokemon: Pokemon):
    if pokemon_id not in pokedex:
        return{
            "message": "Pokemon Not found!",
            "data": {
                "Error": f"Invalid ID: {pokemon_id}"
            }
        }

    delete= pokedex.pop(pokemon_id)
    save_pokedex(pokedex)

    return{
        "message": "Pokemon ID Deleted Successfully!",
        "data": { "Deleted Pokemon Details": delete,
                  "Remaining Pokedex": len(pokedex)
        }
    }