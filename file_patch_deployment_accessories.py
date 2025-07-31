from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict
from utils.file_handler import load_pokedex, save_pokedex

app = FastAPI()

pokedex: Dict[int, dict] = load_pokedex()

class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name")
    level: int = Field(..., ge=5, le=100)
    ptype: str = Field(..., alias="Type")

class PatchPokemon(BaseModel):
    level: Optional[int] = None

class ResponsiveMessage(BaseModel):
    message: str
    data: Optional[Union[Pokemon, str]]

@app.patch(
    "/pokemon/patch/{pokemon_id}",
    response_model=ResponsiveMessage,
    status_code=status.HTTP_200_OK,
    summary="Update Pokémon Level by ID",
    description="""
This endpoint allows you to **update only the level** of a Pokémon by its ID.

✅ Use this if you want to partially modify a Pokémon  
❌ Does NOT change name or type  
⚠️ Level must be between 5 and 100
    """,
    tags=["Patch Operations"],
    response_description="Message and updated Pokémon details if successful"
)
def update_level(pokemon_id: int, patch_data: PatchPokemon):
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokemon with ID {pokemon_id} does not exist."
        )
    
    if patch_data.level is not None:
        pokedex[pokemon_id]["level"] = patch_data.level
        save_pokedex(pokedex)
        
        return {
            "message": "Level Updated Successfully!",
            "data": pokedex[pokemon_id]
        }
