from fastapi import FastAPI, Depends

app = FastAPI()

def get_badge():
    print("🎖️ Badge verified:")
    return "Cascade Badge"

def get_partner(badge: str = Depends(get_badge)):
    print(f"Badge inside partner check: {badge}")
    return "Gengar"

@app.get("/battle")
def start_battle(partner: str = Depends(get_partner)):
    return {"partner": partner}

