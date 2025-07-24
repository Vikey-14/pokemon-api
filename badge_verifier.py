from fastapi import FastAPI,Depends,Query

app=FastAPI()

class BadgeChecker:
    def __init__(self,min_number:int):
        self.min_number=min_number

    def __call__(self, badges: int = Query(...,ge=0, description="Number of badges the trainer has")):
        print(f"Trainer Badges: {badges}.")

        if badges>= self.min_number:
            return f"Trainer accepted with {badges} to enter the gym!"
        
        else: 
            return f"Trainer not authorized to enter since {self.min_number}+ required."
        

@app.get("/gym")
def enter_gym(access: str=Depends(BadgeChecker(min_number=7))):
    return{
        "Status": access
    }
