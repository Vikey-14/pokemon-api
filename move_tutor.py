from fastapi import FastAPI
from typing import Optional

app=FastAPI()

@app.get("/")
def read_root():
    return{"Message": "Welcome to the Move Tutor."}

move_data = {
    "charizard": {
        "signature_moves": ["Flamethrower", "Fly", "Dragon Claw"],
        "level_up_moves": {
            16: "Ember",
            24: "Wing Attack",
            36: "Flamethrower",
            42: "Fire Spin",
            50: "Heat Wave"
        }
    },
    "blastoise": {
        "signature_moves": ["Hydro Pump", "Skull Bash", "Ice Beam"],
        "level_up_moves": {
            16: "Water Gun",
            24: "Bite",
            36: "Surf",
            42: "Rain Dance",
            50: "Hydro Pump"
        }
    }
}

@app.get("/tutor/{pokemon}")
def level(pokemon: str, level: Optional[int]=None):
    pokemon=pokemon.lower()

    if pokemon not in move_data:
        return{"Error": "Enter valid pokemon name."}

    if level is not None:
      available_moves = {
          lvl:move
          for lvl, move in move_data[pokemon]["level_up_moves"].items()
          if lvl<=level
      }
      return{
          "Pokemon": pokemon,
          "Moves up to level": level,
          "Learnable Moves": available_moves or "Moves Not Available at this Level"
    }

    else:
        return{
            "Pokemon": pokemon,
            "Signature Moves": move_data[pokemon]["signature_moves"]
        }