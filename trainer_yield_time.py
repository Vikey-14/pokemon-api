from fastapi import FastAPI, Depends
import time

app = FastAPI()

class TrainerTime:
    def __init__(self):
        self.start_time = None

    def __call__(self):
        self.start_time = time.time()
        trainer_name = "Ash Ketchum"
        print(f"Trainer {trainer_name} has entered the arena at {self.start_time}!")
        yield trainer_name  # <- Return this name to the route
        end = time.time()
        print(f"Trainer {trainer_name} left the arena at {end}. Duration: {round(end - self.start_time, 2)} seconds.")

@app.get("/trainer/time")
def arena_time(trainer: str = Depends(TrainerTime())):
    time.sleep(2)  # Simulating battle duration
    return {"Message": f"{trainer} battled fiercely and exited the arena!"}
