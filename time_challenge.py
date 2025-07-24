from fastapi import FastAPI,Depends,Query,status,HTTPException
import time,random
from typing import Optional

class BadgeValidator():
    def __init__(self):
        self.valid_badge="gym-master"

    def __call__(self, badge: str=Query(...,description="Enter your official badge.")):
        if badge != self.valid_badge:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid badge {badge}! Access Denied!")
        print(f"{badge} Badge verified at {time.strftime('%H%M%S')}")


class GlobalLogger():
    def __call__(self, trainer_name:str=Query(...,regex="^[A-Za-z]{3-20}$", description="Enter your trainer name.")):
        start=time.time()
        print(f"Trainer {trainer_name} entered the arena at {start} seconds.")
        yield 
        end=time.time()
        print(f"Trainer {trainer_name} battle ended at {end}. Duration: {round(end-start,2)} seconds.")


app=FastAPI(dependencies=[Depends(BadgeValidator()), Depends(GlobalLogger())])   

def PokemonSelector(poke:Optional[str]=Query(None,regex="^[A-Za-z]{3,20}$", description= "Enter your partner pokemon name.")):
    if poke:
        print(f"Partner Pokemon of trainer : {poke}")
        return poke


    selected=random.choice(["Gothitelle", "Pikachu", "Lycanroc"])
    print(f"Partner Pokemon: {selected}")
    return selected

@app.get("/trainer/battle")
def battle_arena(partner:str=Depends(PokemonSelector), trainer_name: str = Query(..., description="Enter your trainer name again for response")):
    return{"Message": "Trainer {trainer_name} is authorised to enter the competition.",
           "Partner Pokemon": partner}
