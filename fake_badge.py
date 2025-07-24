from fastapi import FastAPI,Depends,Query,HTTPException,status

app=FastAPI()

class ValidateBadge():
    def __init__(self):
        self.valid_badge="gym-master"
        
        
    def __call__(self, badge:str =Query(...,description="Enter your badge.")):
        if badge!= self.valid_badge:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied! Invalid Badge!")
        print(f"Badge {badge} verified!")
    

@app.get("/trainer")
def trainer(trainer:str=Depends(ValidateBadge)):
    return{"Message": "Trainer is allowed to enter Elite Four!"}


def fake_badge(badge:str= Query(None)):
    print("Test Mode: Skipping real badge check.")
    return True

app.dependency_overrides[ValidateBadge]= fake_badge


