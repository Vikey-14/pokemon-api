from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get("/")

def deep_root():
    return{"Message": "Welcome, Trainer! Ready to catch 'em all?"}

@app.get("/pokemon/{name}")
@app.get("/pokemon")

def get_pokemon(

    name: Optional[str] = None,
    level: Optional[int] = None,
    type: Optional[str] = None
):
    if name is None:
        return{"Error" :  "Please provide a Pokémon name either in path or query."}
    
    return{
        "Name" : name,
        "Level" : level,
        "Type": type
    }