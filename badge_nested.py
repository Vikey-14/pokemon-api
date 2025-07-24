from fastapi import FastAPI,Depends,Query
from typing import Optional
import random

app=FastAPI()

class BadgeChecker():
    def __call__(self, badge: str= Query(...,description="Check's Trainer Badge.")) -> str:
        if badge:
            print(f"Trainer badge: {badge}")
            return badge
        return "Not Qualified to move ahead!"
    
def PartnerSelector(partner: str=Depends(BadgeChecker()))-> Optional[str]:
    if partner != "Not Qualified to move ahead!":
      selected=random.choice(["Lucario", "Gengar", None])
      print(f"Selected Pokemon: {selected}")
      return selected
    return None

@app.get("/badge/partner/battle")
def get_battle(battle: str=Depends(PartnerSelector)):
   if battle is not None:
    return {"Trainer is allowed to battle": battle}
   return {"Trainer is not eligible to battle."}
