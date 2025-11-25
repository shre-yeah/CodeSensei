from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, date
from database import get_database
from auth import get_current_user

router = APIRouter()

@router.post("/lockedin/start")
async def start_locked_in_session(
    problems_required: int,
    time_limit: int = 0,
    db=Depends(get_database),
    current_user=Depends(get_current_user)
):

    if problems_required <= 0:
        raise HTTPException(status_code=400, detail="Problems required must be > 0")

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "mode": "locked_in",
            "locked_in_active": True,
            "locked_in_problems_required": problems_required,
            "locked_in_problems_completed": 0,
            "locked_in_started_at": datetime.utcnow().isoformat(),
            "locked_in_time_limit": time_limit
        }}
    )

    return {"message": "Locked-In session started"}


@router.post("/lockedin/progress")
async def update_progress(
    solved: int,
    db=Depends(get_database),
    current_user=Depends(get_current_user)
):
    user = current_user

    if not user.get("locked_in_active"):
        raise HTTPException(status_code=400, detail="No active session.")

    new_completed = user.get("locked_in_problems_completed", 0) + solved

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"locked_in_problems_completed": new_completed}}
    )

    today_str = date.today().isoformat()

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "locked_in_problems_completed": new_completed,
            "last_coding_date": today_str  
        }}
    )

    # Check if session completed
    if new_completed >= user.get("locked_in_problems_required", 0):
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "locked_in_active": False,
                "mode": "casual"
            }}
        )
        return {"message": "Session complete!"}

    return {"message": "Progress updated"}


@router.post("/lockedin/fail")
async def fail_session(
    db=Depends(get_database),
    current_user=Depends(get_current_user)
):
    user = current_user

    if not user.get("locked_in_active"):
        raise HTTPException(status_code=400, detail="No active session.")

    # Apply penalty
    penalty = user.get("penalty_remaining", 0)

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "xp": max(0, user.get("xp", 0) - penalty),
            "locked_in_active": False,
            "mode": "casual",
            "locked_in_problems_required": 0,
            "locked_in_problems_completed": 0,
            "locked_in_started_at": None,
            "locked_in_time_limit": 0
        }}
    )

    return {"message": "Session failed. Penalty applied."}
