from fastapi import FastAPI,Depends
from typing import Optional
import random

app=FastAPI()

def get_partner()-> Optional[str]:
    return random.choice(["Gengar", "Lucario", None])


@app.get("/duo_battle")
def duo_battle(partner: Optional[str]= Depends(get_partner)):
    
    if partner:
        return{ "Status": f"Trainer has a partner {partner} for battle."  }
    return{"Status": "Trainer has no partner pokemon." }
    
            

    
