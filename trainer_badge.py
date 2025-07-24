from fastapi import FastAPI
from typing import Optional

app= FastAPI()

@app.get("/")
def read_root():
    return{"Message": "Which Trainer's Info You Would Like?"}

trainer_data = {
    "ash": {
        "badges": ["Boulder", "Cascade", "Thunder"],
        "rival": "Gary",
        "hometown": "Pallet Town"
    },
    "misty": {
        "badges": ["Cascade"],
        "rival": "Daisy",
        "hometown": "Cerulean City"
    }
}

@app.get("/trainer/{name}")
def get_trainer(name: str, info: Optional[str]=None):
    name=name.lower()

    if name not in trainer_data:
        return{"Error": "Please enter valid name."}
    
    if info is not None:
        return{
            "Trainer Name": name,
            "Requested Info": trainer_data[name].get(info, "Info Not Available.")

        }
    else:
        return{
            "Trainer Name": name,
            "Hometown": trainer_data[name]["hometown"]
        }



