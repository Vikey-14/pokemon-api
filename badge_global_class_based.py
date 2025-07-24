from fastapi import FastAPI, Query,HTTPException,status,Depends
import time


class ValidateBadge():
    def __init__(self):
        self.valid_badge="gym-master"


    def __call__(self, badge: str=Query(...,description="Enter your Official Trainer Badge.")):
        if badge != self.valid_badge:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access Denied! Invalid Badge!")
        print(f"Badge {badge} verified at {time.strftime('%H%M%S')}")


app=FastAPI(dependencies=[Depends(ValidateBadge)])

@app.get("/pewter")
def Pewter_gym():
    return{"Gym": "Pewter", "Leader": "Brock"}

@app.get("/cerulean")
def Pewter_gym():
    return{"Gym": "Cerulean", "Leader": "Misty"}

@app.get("/lavaridge")
def Pewter_gym():
    return{"Gym": "Lavaridge", "Leader": "Flannery"}

@app.get("/vermilion")
def vermilion_gym():
    return {"Gym": "Vermilion City", "Leader": "Lt. Surge"}

