from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from typing import Dict,Union
from utils.file_handler import load_pokedex, save_pokedex


app=FastAPI()

pokedex: Dict[int, dict] = load_pokedex()

class Pokemon(BaseModel):
    name:str
    ptype:str=Field(...,alias="Type")
    level:int


class ResponseMessage(BaseModel):
    Message: str
    Data: Union[Pokemon,dict]

@app.post("/pokemon", response_model=ResponseMessage)
def create_pokemon(new_pokemon:Pokemon):
    new_id=max(pokedex.keys(), default=0)+1
    pokedex[new_id]= new_pokemon.dict(by_alias=True)
    save_pokedex(pokedex)

    return{
        "Message": "Pokemon Added!",
          "Data": pokedex[new_id]
    }