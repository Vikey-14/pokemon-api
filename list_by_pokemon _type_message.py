from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import List,Dict,Union
from file_handler import load_pokedex

app=FastAPI()

pokedex: Dict[int,dict]= load_pokedex()

class Pokemon(BaseModel):
    name:str=Field(...,alias="poke_name")
    level:int=Field(...,ge=5,le=100)
    ptype:str=Field(...,alias="Type")

class ResponsiveMessage(BaseModel):
    message:str
    data:Dict[str,Union[str,List[Pokemon]]]


@app.get("/pokemon/type/{ptype}", response_model= ResponsiveMessage)
def get_list(ptype:str):
    filtered= [p for p in pokedex.values() 
               if p["Type"]. lower()== ptype.lower()]
    if not filtered:
        return{
            "message": "Pokemon Type Not Found!",
            "data": {"Error": f"Invalid Pokemon Type: {ptype}"}
        }
    message= f"{len(filtered)} Pokemon found with type {ptype.capitalize()}"

    return{
        "message": message,
        "data": {"Pokemon Data": filtered}
    }