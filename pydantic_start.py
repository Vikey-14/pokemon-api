from fastapi import FastAPI
from pydantic import BaseModel 

app= FastAPI()

class Trainer(BaseModel):
    name: str
    age:  int
    region: str


@app.post("/register")
def register_trainer(trainer: Trainer):
    return{
        "Message": f"Trainer {trainer.name} from {trainer.region} has been registered.",
        "Age": trainer.age
    }