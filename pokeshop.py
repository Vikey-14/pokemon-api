from fastapi import FastAPI, Query
from typing import Optional


app= FastAPI()

@app.get("/")
def read_root():
    return{"Message": "Welcome to the Pokeshop Trainers!"}

shop_data = {
    "pokeballs": {
        "effect": "Used to catch Pokémon",
        "price": "200 Pokécoins",
        "stock": 50,
        "description": "Pokeballs are used to catch wild Pokémon."
    },
    "berries": {
        "effect": "Heals status effects",
        "price": "25 Pokécoins",
        "stock": 150,
        "description": "Berries are edible items that help Pokémon recover."
    },
    "potions": {
        "effect": "Restores HP",
        "price": "300 Pokécoins",
        "stock": 120,
        "description": "Potions restore your Pokémon’s health."
    }
}

@app.get("/shop/{category}")

def get_shop(category: str, info: Optional[str]= None):
   category= category.lower()

   if category not in shop_data:
     return{"Error": "Item category not found."}
   
   if info is not None:
     return{
       "Category": category,
       "Requested Info": shop_data[category].get(info, "Info type not available.")
     }
   else:
     return{
       "Category": category,
       "Description": shop_data[category]["description"]
     }
       

     

