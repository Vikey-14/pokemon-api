from fastapi import FastAPI,Query,Depends,HTTPException,status
import time


def validate_badge(badge: str=Query(..., description="Enter your offical Trainer Badge.")):
    if badge != "gym-master":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access Denied! Invalid Badge!")
    print(f"Badge {badge} verified at {time.strftime('%H%M%S')}")
    
app=FastAPI(dependencies=[Depends(validate_badge)])

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

