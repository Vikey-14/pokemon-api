from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

class Pokemon(BaseModel):
    name: str
    level: int
    ptype: str

class Trainer(BaseModel):
    name: str
    age: int
    region: str
    team: list[Pokemon]

@app.post("/trainer")
def register_trainer(trainer: Trainer):
    return{
        "Name": trainer.name,
        "Region": trainer.region,
        "Pokemon Count": len(trainer.team),
        "Pokemon Team":trainer.team
    }