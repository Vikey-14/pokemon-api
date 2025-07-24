from fastapi import FastAPI, Query


app = FastAPI()

@app.get("/")


def read_root():
    return{"Message": "Hello, Commander V! Your FastAPI journey begins."}

@app.get("/trainer")

def get_trainer(name: str = Query(..., min_length=3, max_length=20,description= "Trainer's name")):
    return{"Trainer" : name}

