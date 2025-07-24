from fastapi import FastAPI,Depends,Query
import time

app=FastAPI()

class TrainerLogger():
    def __init__(self):
        self.weather="Stormy"
        

    def __call__(self, badges: str=Query(...,ge=0,le=8,description="Number of badges the trainer has.")):
        print("Trainer Alert: Trainer has entered the arena!!!")
        print(f"Weather alert: {self.weather}")
        print(f"Number of Badges: {badges}! Access Granted!!!")
        print(f"Arrival Time: {time.strftime('%H%M%S')}")


@app.get("/trainer", dependencies=[Depends(TrainerLogger())])
def enter_battle():
    return{"Message": "The trainer is ready to take on the Pokemon League!"}