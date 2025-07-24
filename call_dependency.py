from fastapi import FastAPI,Depends

app=FastAPI()


class RainChecker:

    def __init__(self, min_level:int):
        self.min_level= min_level


    def __call__(self):
        trainer_level=12
        print(f"Trainer Level: {trainer_level}")
        
        if trainer_level >= self.min_level:
            return f"Access Granted for level {trainer_level} trainer."
        else:
            return f"Access Denied! Level {self.min_level}+ required."
        
        
@app.get("/gym/")
def enter_gym(access: str=Depends(RainChecker(min_level=15))):
    return{
        "Status": access
    }