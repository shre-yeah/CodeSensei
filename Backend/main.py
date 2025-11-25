from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from database import connect_to_mongo, close_mongo_connection, get_database
from schemas import UserResponse
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router  
from streaks import router as streak_router 
from ai_chat import router as ai_chat_router


import os
import uvicorn



app = FastAPI(title="User Authentication API")

origins = [
    "http://localhost:5173", # Vite (React) default port
    "http://localhost:3000", # Create React App default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allows these specific origins
    allow_credentials=True,      # Allows cookies/auth headers
    allow_methods=["*"],         # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allows all headers
)


app.include_router(streak_router)
app.include_router(ai_chat_router)

@app.get("/", tags=["Root"])
async def root():
    """Bro this is where the dsa application startsss"""
    return {
        "message": "Loginn pagee thing for dsa appp",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /auth/register",
            "login_json": "POST /auth/login",
            "login_form": "POST /auth/token",
            "current_user": "GET /auth/me",
            "protected": "GET /auth/protected"
        }
    }


# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    print("Connected to MongoDB Atlas! yay!")
    
@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    print("Closed MongoDB connection! Yay!")

# Public routes
# Include routers
app.include_router(auth_router)



# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if API is running"""
    return {"status": "healthy", "message": "API is running"}

# Run the application
if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)