from fastapi import FastAPI
from pydantic import BaseModel, Field, conlist
from typing import Optional, List, Annotated

app=FastAPI()

class Evolution(BaseModel):
    current_stage: str
    next_stage: Optional[str]= None
    evolution_level: Optional[int]= None


class Pokemon(BaseModel):
    name: str
    ptype: str
    level: int= Field(..., ge=50, le=100, description= "Level must be between 50 and 100")
    nickname: Optional[str]= None
    held_item: Optional[str]= None
    evolution: Optional[Evolution]= None

class EliteTrainer(BaseModel):
    name: str
    region: str
    team: Annotated[List[Pokemon], conlist(Pokemon,max_length=6)]


@app.post("/elite_register")
def register_elite_trainer(trainer: EliteTrainer):
    summary= []

    for p in trainer.team:
        poke_summary = f"{p.name}  (Level {p.level})"

        if p.nickname:
            poke_summary+= f" also known as '{p.nickname}'"

        if p.held_item:
            poke_summary+= f" is holding {p.held_item}"

        if p.evolution:
            poke_summary+= f". It evolved from {p.evolution.current_stage}"
            if p.evolution.next_stage:
                poke_summary+= f" and may evolve into {p.evolution.next_stage}"

            if p.evolution.evolution_level:
                poke_summary+= f" at level {p.evolution.evolution_level}."

    summary.append(poke_summary)
    
    return{

        "Trainer": trainer.name,
        "Region": trainer.region,
        "Team Size": len(trainer.team),
        "Pokemon Summary": summary
    }