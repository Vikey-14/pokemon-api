from fastapi import FastAPI,HTTPException,status,Query
from pydantic import BaseModel,Field
from typing import Optional,Dict,List,Union
from file_handler import load_pokedex, save_pokedex

app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class ResponsiveMessage(BaseModel):
    message: str
    data: Union[Pokemon,str,List[dict]]

@app.get("/pokemon/{pokemon_id}", response_model= ResponsiveMessage, status_code=status.HTTP_200_OK, tag=["Trainer View"])
def get_pokemon_id(pokemon_id:int,
                   
                   name: Optional[str]= Query(None, description="Search by Pokemon Name."),
                   level: Optional[int]= Query(None, description="Search by Pokemon Level."),
                   ptype: Optional[str]= Query(None, description="Search by Pokemon Type.")
                   ):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid ID {pokemon_id}.")
    
    pokemon= pokedex[pokemon_id]

    if name and name.lower() != pokemon["poke_name"].lower():
        return {
            "message": f"Name filter {name} does not match Pokémon ID {pokemon_id}.",
            "data": []
        }
    if ptype and ptype.lower() != pokemon["Type"].lower():
        return {
            "message": f"Type filter {ptype} does not match Pokémon ID {pokemon_id}.",
            "data": []
        }
    if level != pokemon["level"]:
        return {
            "message": f"Level filter {level} does not match Pokémon ID {pokemon_id}.",
            "data": []
        }
    
    return {
        "message": "Pokemon found with all filters applied!",
        "data": pokemon
    }
    
    

    
    
    
