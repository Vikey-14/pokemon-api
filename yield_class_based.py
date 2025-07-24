from fastapi import FastAPI, Depends
import time


app=FastAPI()

class TrainerTime():
    def __init__(self):
     self.start_time= None

    def __call__(self):
        self.start_time=time.time()
        print(f"Trainer has entered the arena at {self.start_time}!")
        yield
        end=time.time()
        print(f"End time {end}, Duration= {round(end-self.start_time,2)} seconds.")

@app.get("/trainer/time", dependencies=[Depends(TrainerTime())])
def arena_time():
   time.sleep(2)
   return{"Message": "Trainer battled and left the arena."}
