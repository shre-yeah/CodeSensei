from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from auth import get_current_user
from database import get_database
from locked_in import update_locked_in_status

# Import your rule engine components
from rule_engine.nlp_preprocessing import NLPPreprocessor
from rule_engine.dsa_recommender import DSARecommender
from rule_engine.response_generator import ResponseGenerator

router = APIRouter()

# Initialize rule engine (only once)
preprocessor = NLPPreprocessor()
recommender = DSARecommender()
generator = ResponseGenerator()


class ChatRequest(BaseModel):
    user_input: str


@router.post("/chat")
async def chat_with_sensei(request: ChatRequest,
                           db=Depends(get_database),
                           current_user=Depends(get_current_user)):
    """
    Unified AI chat endpoint for CodeSensei
    """
    user_id = current_user["_id"]
    user_input = request.user_input
    #Save user's message
    await save_chat_message(db, user_id, "user", user_input)

    # STEP 1: Parse input using your rule engine
    parsed = preprocessor.process_user_input(user_input)

    if not parsed:
        return {"message": "Hmm, I couldn't understand that clearly. Could you try rephrasing?"}

    intent = parsed.get("intent")

    difficulty = None
    xp_gain = None

    # STEP 2 — Handle intents using your existing rule logic

    if intent == "learned_concept":
        data = recommender.recommend_from_concepts(parsed["concepts"])
        response = generator.generate_concept_learned_response(data)
        response = generator.add_motivational_footer(response)

        # For learned concepts, we don't award XP (or use a default)
        # Only award streak
        await update_streak(db, current_user)

        

    # USER SOLVED A PROBLEM
    elif intent == "solved_problem":
        problem = parsed["problems"][0]
        data = recommender.recommend_from_problem(problem)
        
        # Check if problem was found
        if "error" in data:
            return {"message": data.get("error", "Problem not found")}
        
        # Get the difficulty from the solved problem
        # The recommender needs to return this - let me show you how to fix it
        else:

            difficulty = data.get("difficulty", "medium")  # Default to medium if not found
        
            response = generator.generate_problem_solved_response(data, problem)
            response = generator.add_motivational_footer(response)

         # 🔥 Update locked-in mode status
        user = await update_locked_in_status(db, current_user)

        # 🔥 If penalty active, reduce it
        if user["mode"] == "locked_in" and user.get("penalty_remaining", 0) > 0:
            new_penalty = user["penalty_remaining"] - 1

            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {"penalty_remaining": new_penalty}}
            )

            response += f"\n\n⚡ Locked-In Progress: {new_penalty} problems left for today."

            if new_penalty == 0:
                response += "\n🎉 You cleared today's Locked-In penalty! Beast mode!!"


        # Award streak and XP
        await update_streak(db, current_user)
        xp_gain = await add_xp_anytime(db, current_user, difficulty)
        
        
    else:
        response = "I'm not quite sure how to help with that. Could you provide more details?"
    # 2 Save AI assistant message ONCE (outside the if/elif)
    await save_chat_message(db, user_id, "assistant", response)

    # 3 Return final unified response
    result = {"message": response}
    if difficulty:
        result["difficulty"] = difficulty
    if xp_gain:
        result["xp_gained"] = xp_gain
    return result
  

async def update_streak(db, current_user):
    """Increase streak only once per day"""
    user = await db.users.find_one({"_id": current_user["_id"]})

    today = date.today().isoformat()
    last_active = user.get("last_active_date")

    # Only update if user hasn't checked in today
    if last_active != today:
        new_streak = user.get("streak", 0) + 1

        await db.users.update_one(
            {"_id": current_user["_id"]}, 
            {
                "$set": {
                    "streak": new_streak,
                    "last_active_date": today
                }
            }
        )
        print(f"Updated streak to {new_streak} for user {current_user['name']}")


async def add_xp_anytime(db, current_user, difficulty):
    """Award XP based on activity difficulty anytime"""
    
    xp_values = {
        "easy": 10,
        "medium": 20,
        "hard": 40
    }

    xp_gain = xp_values.get(difficulty, 10)

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            
            "$inc": {"xp": xp_gain},
            "$set": {"last_coding_date": date.today().isoformat()}
        }
    )
    print(f"Awarded {xp_gain} XP to user {current_user['name']} for {difficulty} activity.")
    return xp_gain


async def save_chat_message(db, user_id, role, message):
    await db.chat_logs.insert_one({
        "user_id": user_id,
        "role": role,  # "user" or "assistant"
        "message": message,
        "timestamp": datetime.utcnow()
    })
