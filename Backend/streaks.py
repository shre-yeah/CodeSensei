from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date, datetime, timedelta
from database import get_database
from schemas import UserResponse
from auth import get_current_user

router= APIRouter(prefix="/streaks", tags=["Streak Tracking"])

XP_PER_CHECKIN= 10

@router.post("/checkin", response_model= UserResponse)
async def checkin(
    user: dict= Depends(get_current_user),
    db = Depends(get_database)
    ):
    """Updates user streak, xp, and last_active_date."""

    user_id= user["_id"]
    today= date.today()

    #Fetch fresh records from DB

    db_user = await db.users.find_one({"_id": user_id})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    last_active=  db_user.get("last_active_date")

    
    # Normalize last_active to a date or None
    if last_active is None:
        last_active_date = None
    elif isinstance(last_active, str):
        last_active_date = date.fromisoformat(last_active)
    elif isinstance(last_active, datetime):
        last_active_date = last_active.date()
    elif isinstance(last_active, date):
        last_active_date = last_active
    else:
        last_active_date = None
    
    streak = db_user.get("streak", 0)
    xp= db_user.get("xp", 0)
    total_checkins= db_user.get("total_checkins", 0)

    #Streak logic

    if last_active == today:
        #User already checked in today
        pass
    else:
        if last_active == today - timedelta(days=1):
            # Increment streak normally
            streak += 1
        else:
            # Streak broken
            streak = 1

        xp += XP_PER_CHECKIN
        total_checkins += 1

        # Update DB
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "streak": streak,
                    "xp": xp,
                    "total_checkins": total_checkins,
                    "last_active_date": today.isoformat()
                }
            }
        )
    
    # Return updated user data
    updated_user = await db.users.find_one({"_id": user_id})

    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        created_at=updated_user["created_at"],
        streak=updated_user["streak"],
        xp=updated_user["xp"],
        total_checkins=updated_user["total_checkins"],
        last_active_date=updated_user.get("last_active_date")
    )
           
