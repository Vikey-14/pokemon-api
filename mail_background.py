from fastapi import FastAPI,BackgroundTasks
from datetime import datetime
import json
import os

app=FastAPI()

MAILBOX= "pokemail.json"

def send_pokemail(trainer_name:str, message:str):
    mail={
        "Trainer": trainer_name,
        "Message": message,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if not os.path.exists(MAILBOX):
        with open(MAILBOX, "w")as f:
            json.dump([],f)


    with open(MAILBOX, "r+")as f:
        mailbox= json.load(f)
        mailbox.append(mail)
        f.seek(0)
        json.dump(mailbox,f, indent=4)


@app.post("/poke-center/mail")
def poke_mail(trainer:str, pokemon:str, background_tasks: BackgroundTasks):
    msg=f"Dear {trainer}, your Pokémon {pokemon} is now healthy and ready to battle!"
    background_tasks.add_task(send_pokemail,trainer,msg)

    return{
        "Message": f"{pokemon} is healing... You will receive a PokéMail shortly, {trainer}!"
    }