from fastapi import FastAPI, Depends

app = FastAPI()

# ✅ This function returns the trainer's name
def get_trainer_name():
    print("👤 Trainer identified as Ash")
    return "Ash"

# ✅ This route receives that name via Depends
@app.get("/whoami")
def who_am_i(trainer: str = Depends(get_trainer_name)):
    return {"trainer_name": trainer}
