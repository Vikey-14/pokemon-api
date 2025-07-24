from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return{"Message": "Welcome, Trainer! Ready to catch 'em all?"}

@app.get("/pokemon/{poke_id}")
def get_pokemon(poke_id: int, details: Optional[str]= None):
    return{"Pokemon ID" : poke_id,
            "Requested_Info": details or "basic data"
           }