from datetime import date, timedelta

async def update_locked_in_status(db , user: dict) -> dict:
    """Update missed days + penalties for locked-in mode."""

    # Only apply logic if locked_in_mode
    if user.get("mode") != "locked_in":
        return user  # Nothing to do

    today = date.today()
    today_str = today.isoformat()

    last_date_str = user.get("last_coding_date")
    weekly_reset_date_str = user.get("weekly_reset_date")

    # Weekly reset every Monday
    if today.weekday() == 0:  # Monday = 0
        #Only run reset once a week, on monday that is
        if weekly_reset_date_str != today_str:
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "missed_days": 0,
                    "penalty_remaining": 0,
                    "weekly_reset_date": today_str
                }}
            )
        return await db.users.find_one({"_id": user["_id"]})

    # First-ever day using locked in mode
    if last_date_str is None:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_coding_date": today_str}}
        )
        return await db.users.find_one({"_id": user["_id"]})

    # Calculate missed days
    last_date = date.fromisoformat(last_date_str)
    delta = (today - last_date).days

    if delta > 1:
        missed = delta - 1
        new_missed = user.get("missed_days", 0) + missed
        new_penalty = 2 ** new_missed

        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "missed_days": new_missed,
                "penalty_remaining": new_penalty,
                "last_coding_date": today_str
            }}
        )
    
    return await db.users.find_one({"_id": user["_id"]})
