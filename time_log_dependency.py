from fastapi import FastAPI,Depends
import time


app=FastAPI()

def log_battle_entry():
    print(f"Trainer accessed the stadium at {time.strftime("%H:%M:%S")}")


@app.get("/trainer/log", Dependencies=[Depends(log_battle_entry)])
def enter_battle():
    return{"Message": "Trainer has entered the stadium."}
