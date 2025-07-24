from fastapi import FastAPI, BackgroundTasks

app=FastAPI()

def trainer_log(trainer: str):
    with open("trainer_logs.txt", "a")as f:
        f.write(f"Trainer {trainer} visited the Pokemon Center.\n")


@app.get("/visit")
def visit(name: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(trainer_log,name)
    return{"Message": f"Welcome{name},Nurse Joy will heal your Pokemon shortly!"}
