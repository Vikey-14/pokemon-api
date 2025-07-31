from fastapi import FastAPI,Path,HTTPException,status
from pydantic import BaseModel,Field
from utils.file_handler import load_pokedex
from typing import List,Dict,Optional,Union


app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()


class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    ptype:str=Field(...,alias="Type")
    region:str
    level:int=Field(...,ge=5,le=100)


class ResponsiveMessage(BaseModel):
    message:str
    data: Union[List[Pokemon],str]


@app.get("/pokemon/{region}", response_model=ResponsiveMessage, status_code=status.HTTP_200_OK, description= "Provides pokemon info by region name provided.", response_description="List of Pokémon objects or not-found message")
def get_pokemon_by_region(region:str=Path(..., regex="^[A-Za-z]{3,20}$", title="Pokemon provided by region name", description= "Only alphabets and numerics allowed within 3-20 string range."), pokemon= Pokemon):
   matching=[
      pokemon for pokemon in pokedex.values()
      if pokemon.get("region", "").lower() == region.lower()

   ]
   if not matching:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid pokemon region name: {region}")
      

   return{
    "message": f"{len(matching)} Pokemon fond of {region} region.",
    "data": matching
   }
    