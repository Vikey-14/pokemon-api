from fastapi import FastAPI,HTTPException,status,Query
from pydantic import BaseModel,Field
from typing import List,Dict,Union,Optional
from file_handler import load_pokedex, save_pokedex


app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class PatchPokemon(BaseModel):
    level:Optional[int]= None

class ResponsiveMessage(BaseModel):
    message:str
    data:Union[Pokemon,str,List[dict]]

@app.patch("/pokemon/info/{pokemon_id}",response_model=ResponsiveMessage,status_code=status.HTTP_200_OK,tags=["Admin Actions"],
        summary="Update level of Pokemon.", description="Updates a Pokémon's level after verifying name/type via query params.",
        response_description= "Message and data present the pokemon data or display the error upon wrong input provided."
         )
def update_pokemon_info(pokemon_id:int, patch_data: PatchPokemon,
                     name:str=Query(None, description="Verify Pokemon Name."),
                     ptype:str=Query(None, description="Verify Pokemon Typing.")
                     ):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid ID- {pokemon_id} provided.")
        
        
    pokemon= pokedex[pokemon_id]


    if name and name.lower() != pokemon["poke_name"].lower():
        return{
            "message": f"Name Filter {name} does not match the Pokemon ID {pokemon_id}",
            "data": "Update Aborted."
        }
    
    if ptype and ptype.lower() != pokemon["Type"].lower():
        return{
            "message": f"Type Filter {ptype} does not match the Pokemon ID {pokemon_id}",
            "data": "Update Aborted."
        }
        
    if patch_data.level is not None:
        pokemon["level"]= patch_data.level
        save_pokedex(pokedex)
        
        return {"message": "Level Updated Successfully.", "data": pokemon}
    
    return {"message": "No changes made.", "data": pokemon}



    



