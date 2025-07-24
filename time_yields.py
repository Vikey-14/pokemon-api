from fastapi import FastAPI,Depends
import time


app=FastAPI()

def timer_dependency():
    start=time.time()
    print("Timer Started")

    yield
    end=time.time()
    print(f"Timer Ended! Duration: {round(end-start,2)} seconds.")


@app.get("/trainer/entry", dependencies=[Depends(timer_dependency)])
def mission_entry():
    time.sleep(2)
    return{"Message": "Mission Completed Successfully!"}
