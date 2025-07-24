from fastapi import APIRouter, Depends
from auth.security import verify_token

router= APIRouter()

@router.get("/trainer/profile", tags=["Trainer View"], summary="View Trainer Profile", description="Only accessible with a valid token.")
async def get_trainer_profile(current_user: str = Depends(verify_token)):
    return {
        "trainer": current_user,
        "message": f"Welcome back, {current_user.capitalize()}! Here's your profile data.",
        "badges": ["Boulder", "Cascade", "Thunder", "Rainbow"]
    }
