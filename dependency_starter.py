from fastapi import FastAPI,Depends

app=FastAPI()

def starter():
    print("Checking for selected starter pokemon...")
    return("Charmander")

@app.get("/pokemon")
def starter_pokemon(starter: str=Depends(starter)):
    return{
        "🔥Starter selected": starter
    }