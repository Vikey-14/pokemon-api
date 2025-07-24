from fastapi import FastAPI, Request

app =FastAPI()

@app.post("/register")
async def register_trainer(data: dict):
    Name= data.get("name")
    Age= int(data.get("age"))
    Region=data.get("region")

    return{
        "Message": f"Trainer {Name} from {Region} region has been registered successfully. ",
        "Age": Age
    }
