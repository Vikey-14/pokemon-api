from fastapi import FastAPI

app=FastAPI()

evolution_data = {
    "charmander": {"evolution": "Charmeleon", "level": 16},
    "charmeleon": {"evolution": "Charizard", "level": 36},
    "squirtle": {"evolution": "Wartortle", "level": 16},
    "wartortle": {"evolution": "Blastoise", "level": 36},
    "bulbasaur": {"evolution": "Ivysaur", "level": 16},
    "ivysaur": {"evolution": "Venusaur", "level": 32}
}
@app.post("/evolution")
async def evolve(data: dict):
    name= data.get("name", "").lower()
    level= int(data.get("level", 0))

    if name not in evolution_data:
        return{
            "Message": f"{name.title()} not in Evolution Data."
        }
    
    required_level= evolution_data[name]["level"]
    next_form= evolution_data[name]["evolution"]

    if level>= required_level:
        
                  message=  f"{name.title()} has evolved into {next_form} at level {level}."
            
                  if next_form.lower() in evolution_data:
                   next_evo=evolution_data[next_form.lower()]
                  levels_left=next_evo["level"]- level

                  if levels_left>0:
                       message += f"It needs {levels_left} more level(s) to evolve into {next_evo["evolution"]}."
                       return{"Message": message}
    else:
       return{
            "Message": f"{name.title()} has to train more to level up and evolve."
        }