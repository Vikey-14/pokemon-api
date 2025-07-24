from fastapi import FastAPI, Request

app =FastAPI()

@app.post("/evolution")
async def evolve(data: dict):
    name=data.get("name")
    level=int(data.get("level"))
    evolution= data.get("evolution")

    if level>=36:
        return{
            "Message": f"{name} has evolved into {evolution} at level {level}"
        }
    else:
        return{
            "Message": f"{name} is not ready to evolve. Needs more training."
        }