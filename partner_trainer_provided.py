from fastapi import FastAPI, Depends,Query
from typing import Optional
import random

app =FastAPI()

class PartnerSelector():
    def __call__(self, poke: Optional[str] = Query(default=None, description="Enter your partner Pokémon")) -> Optional[str]:
     if poke:
       print(f"Trainer's partner pokemon: {poke}.")
       return poke
           
           
     partner=random.choice(["Lucario", "Armaldo", None])
     print(f"Trainer's partner pokemon: {partner}")
     return partner 

@app.get("/battle/partner")
def get_partner(partner: Optional[str]= Depends(PartnerSelector())):
  if partner:
    return{"Info": f"Trainer has the following {partner} as the partner pokemon."}
  return{"Info": f"Trainer has no partner pokemon."}