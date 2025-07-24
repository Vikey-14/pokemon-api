from fastapi import FastAPI, Depends
import time

# Global logger dependency
def global_logger():
    print(f"[🕒] Request hit at {time.strftime('%H:%M:%S')}")

# Add the dependency globally across all routes
app = FastAPI(dependencies=[Depends(global_logger)])

@app.get("/home")
def home():
    return {"Message": "Welcome to the Pokémon League!"}

@app.get("/trainer")
def trainer():
    return {"Trainer": "Ash Ketchum"}

@app.get("/pokemon")
def pokemon():
    return {"Pokémon": ["Pikachu", "Charizard", "Bulbasaur"]}
