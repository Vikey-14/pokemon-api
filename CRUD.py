from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import Optional, Dict,Union,List
from file_handler import load_pokedex, save_pokedex


app=FastAPI()


pokedex: Dict[int, dict] = load_pokedex()


class Pokemon(BaseModel):
    name:str
    ptype:str=Field(...,alias="Type")
    level:int

class ResponseMessage(BaseModel):
    message:str
    data: Union[Pokemon, List[Pokemon], dict]


class PatchPokemon(BaseModel):
    name:Optional[str]= None
    ptype:Optional[str]=Field(default=None, alias="Type")
    level:Optional[int]= None


@app.post("/pokemon", response_model=ResponseMessage)
def create_pokemon(new_pokemon:Pokemon):
   new_id=max(pokedex.keys(), default=0)+1
   pokedex[new_id]= new_pokemon.dict(by_alias=True)
   save_pokedex(pokedex)

   return {
        "message": "Pokemon Added!", "data": pokedex[new_id]
   }

@app.get("/pokemon",response_model=ResponseMessage)
def get_all_pokemon():
    return{
       "message": "All Pokémon retrieved successfully!",
         "data": list(pokedex.values())
   }

@app.get("/pokemon/{pokemon_id}",response_model=ResponseMessage)
def get_one_pokemon(pokemon_id: int):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon Not Found.")
  
    return {
   "message": f"Pokémon with ID {pokemon_id} retrieved!",
   "data": pokedex[pokemon_id]
}


@app.put("/pokemon/{pokemon_id}",response_model=ResponseMessage)
def put_pokemon(pokemon_id:int, updated:Pokemon):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon Not Found.")
    
    pokedex[pokemon_id]= updated.dict(by_alias=True)
    save_pokedex(pokedex)
    
    return{"message": "Pokedex Updated!", "data": pokedex[pokemon_id] }

@app.patch("/pokemon/{pokemon_id}",response_model=ResponseMessage)
def patch_pokemon(pokemon_id: int, patched: PatchPokemon):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon Not Found.")
    
    for field,value in patched.dict(exclude_unset=True).items():
        pokedex[pokemon_id][field]= value

    save_pokedex(pokedex)

    return{
        "message": "Pokedex Partially Updated", "data": pokedex[pokemon_id]
    }

@app.delete("/pokemon/{pokemon_id}",response_model=ResponseMessage)
def delete(pokemon_id: int):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=404, detail="Pokemon Not Found.")

    deleted_pokemon=pokedex.pop(pokemon_id)
    save_pokedex(pokedex)

    return {
    "message": f"Pokémon ID {pokemon_id} deleted successfully.",
    "data": {
        "deleted": deleted_pokemon,
        "remaining": pokedex
    }
}
