from fastapi import FastAPI
from pydantic import BaseModel

app= FastAPI()

class Pokemon(BaseModel):
    name: str
    level: int
    ptype: str
    ability: str

@app.post("/registration")
def pokemon_register(pokemon: Pokemon):
    return{
        "Message": f"{pokemon.name} (Type:{pokemon.ptype}) with ability {pokemon.ability} has been registered at level-{pokemon.level}. ",
        "Details": pokemon
    }
