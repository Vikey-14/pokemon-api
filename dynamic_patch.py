from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel,Field
from typing import Optional,List,Dict,Union
from utils.file_handler import load_pokedex, save_pokedex


app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class PatchPokemon(BaseModel):
    level:Optional[int]=None

class ResponsiveMessage(BaseModel):
    message:str
    data: Optional[Union[Pokemon,str]]

@app.patch("/pokemon/patch/{pokemon_id}", response_model= ResponsiveMessage, status=status.HTTP_200_OK)
def update_level(pokemon_id: int, patch_data: PatchPokemon):
    if pokemon_id not in pokedex:
        raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Pokemon with ID {pokemon_id} does not exist."
        )
    if patch_data.level is not None:
        pokedex[pokemon_id]["level"]= patch_data.level
        save_pokedex(pokedex)

        return{
            "message": "Level Updated Successfully!",
            "data": pokedex[pokemon_id]
        }

