from fastapi import FastAPI,Depends
from typing import Optional
import random


app=FastAPI()

class PartnerSelector:
    def __call__(self)-> Optional[str]:
        partner=random.choice(["Gengar", "Lucario", None])
        print(f"Selected Partner: {partner}")
        return partner
    

@app.get("/partner")
def get_partner(part: Optional[str]= Depends(PartnerSelector())):
    if part:
        return{"Status": f"The trainer has following {part} pokemon."}
    return{"Status": "Trainer has chosen no partner pokemon."}