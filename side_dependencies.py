from fastapi import FastAPI,Depends
import time

app=FastAPI()

def announce_trainer():
    print("The trainer has entered the battle arena!")

def arrival_time():
    print(f"The trainer arrived at{time.strftime('%H%M%S')}")

def weather():
    print("Weather conditions at the moment at : Stormy.")

def verify_badge():
    print("Verifying trainer has 8 badges... Access granted!")


@app.get("/trainer", dependencies=[Depends(announce_trainer), Depends(arrival_time), Depends(weather), Depends(verify_badge)])
def enter_battle():
    return{"Message": "The Trainer is now entering the Pokemon League!"}

    


















