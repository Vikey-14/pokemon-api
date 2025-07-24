from fastapi import FastAPI

app=FastAPI()

@app.post("/register")
async def register_pokemon(data: dict):

    name= data.get("name")
    poke_type= data.get("type")
    level= int(data.get("level"))
    ability=data.get("ability")

    return{

        "Message": f"Pokemon {name}, ({poke_type}) with ability {ability} registered at level{level}. ",
        "Level": level
    }
    