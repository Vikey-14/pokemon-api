from fastapi import FastAPI,Depends,Query
from typing import Optional
import random,time,uuid

app=FastAPI()

class GlobalLogger():
    def __call__(trainer: str=Query(...,regex="^[A-Za-z]{3,20}$", description="Enter your trainer name.")):
        start=time,time()
        print(f"Trainer {trainer} has arrived at {start} seconds.")
        try:
            yield trainer
        finally:
            end=time.time()
            print(f"Trainer left the arena at {end} seconds.")
            print(f" Duration of trainer stay: {round(end-start,2)} seconds.")


def BattleMonitor():
    match_id=str(uuid.uuid4())[:8]
    print(f"Match id: {match_id}- Battle Initiated. ")
    try:
        yield match_id
    finally:
        print(f"Match id: {match_id}- Battle Concluded. ")


def PartnerSelector(poke:Optional[str]=Query(None,regex="^[A-Za-z]{3,20}$", description="Enter your partner pokemon name.")):
    if poke:
        print(f"Trainer's Partner Pokemon: {poke}")
        return poke

    selected=random.choice(["Lucario", "Pikachu", "Magikarp"])
    print(f"Trainer's Partner Pokemon: {selected}")
    return selected



@app.get("/battle/arena")
def battle_arena(trainer: str=Depends(GlobalLogger()), match_id: str=Depends(BattleMonitor), partner: str=Depends(PartnerSelector)):
    time.sleep(2)
    return{
        "Trainer": trainer,
         "Match ID": match_id,
         "Partner Pokemon": partner,
         "Message": f"Battle Completed! Good Job {trainer}"
 }

            
    



    