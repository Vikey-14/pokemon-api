from fastapi import FastAPI,Depends,Query

app=FastAPI()


def get_trainer_name(trainer:str=Query(...,regex="^[A-Za-z]{3,20}$", description="Enter your trainer name.")):
    return trainer


@app.get("/trainer")
def get_trainer(trainer:str=Depends(get_trainer_name)):
    return{"Message": f"Trainer {trainer} is ready to battle!"}


def fake_trainer_name():
    return "Red"

app.dependency_overrides[get_trainer_name]= fake_trainer_name
