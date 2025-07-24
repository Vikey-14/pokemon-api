from fastapi import FastAPI,BackgroundTasks
from datetime import datetime

app=FastAPI()

def healing_log(trainer:str, pokemon:str):
    with open("healing_logs.txt", "a")as f:
        now= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] Trainer {trainer} healed {pokemon} at the Pokemon Center.\n")


@app.get("/heal")
def healing(name:str, poke: str, background_tasks:BackgroundTasks):
    background_tasks.add_task(healing_log,name,poke)
    return{"Message": f"{poke} is being healed! Nurse joy sends her regards to {name}."}

    