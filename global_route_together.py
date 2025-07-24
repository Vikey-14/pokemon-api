from fastapi import FastAPI,Query,Depends,HTTPException,status
import time, random
from typing import List

class Validate_Badge():
    def __init__(self, ):
        self.valid_badge="gym-master"

    def __call__(self, badge: str=Query(...,description="Enter your official Pokemon Badge.")):
      if badge != self.valid_badge:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                           detail="Access Denied! Invalid Badge!")
        print(f"Badge {badge} validated at {time.strftime('%H%M%S')}")

class TrainerLogger():
    
    def __call__(self, weather: str=Query(..., description="Enter curret weather condition.")):
        print(f"Trainer arrived at {time.strftime('%H%M%S')}")
        print(f"Curretn weather at Indigo Plateau: {weather}")
        print("Awaiting Confrimation!!!")

app=FastAPI(dependencies=[Depends(Validate_Badge()), Depends(TrainerLogger())])

def TeamSelector()-> List[str]:
    selected=random.sample[("Lucario","Pikachu","Mankey","Roselia", "Wailord"),3]
    print(f"Selected Team : {selected}")
    return selected


@app.get("/battle_arena/")
def get_trainer(team: List[str]= Depends(TeamSelector)):
    return{  "message": "Trainer is ready for battle!",
        "Team Assigned": team}

    
