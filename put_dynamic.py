from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import Dict,Optional,List,Union
from file_handler import load_pokedex, save_pokedex

app=FastAPI()

pokedex: Dict[int, dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class ResponsiveMessage(BaseModel):
    message:str
    data: Union[Pokemon,str]


@app.put("/pokemon/put/{pokemon_id}", response_model= ResponsiveMessage)
def update_or_create_pokemon(pokemon_id:int, update_pokemon: Pokemon):
   
   pokedex[pokemon_id]= update_pokemon.dict(by_alias=True)
   save_pokedex(pokedex)

   message= ( "Pokemon ID Updated Successfully!" if pokemon_id in pokedex else "New Pokemon Created Successfully!")

   return{
       "message": message,
       "data": pokedex[pokemon_id]

   }


