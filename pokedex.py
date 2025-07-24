from fastapi import FastAPI
from typing import Optional


app= FastAPI()

@app.get("/")
def read_root():
    return{"Message": "Welcome to the Pokedex Trainers! How can i help you?"}

pokedex = {
    "pikachu": {
        "type": "Electric",
        "evolution": "Raichu",
        "ability": "Static",
        "description": "Mouse Pokémon that stores electricity in its cheeks."
    },
    "bulbasaur": {
        "type": "Grass/Poison",
        "evolution": "Ivysaur",
        "ability": "Overgrow",
        "description": "A seed Pokémon with a plant growing on its back."
    }
}

@app.get("/pokedex/{pokemon}")
def get_pokedex(pokemon: str, info: Optional[str]= None):
    pokemon=pokemon.lower()

    if pokemon not in pokedex:
     return{"Error": "Please Enter Valid Name."}

    if info is not None:
       return{
          "Pokemon": pokemon,
          "Requested Info": pokedex[pokemon].get(info, "Info Not Available.")

       }
    else:
            return{
            "Pokemon": pokemon,
          "Description": pokedex[pokemon]["description"]
            }
