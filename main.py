from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from database import connect_to_mongo, close_mongo_connection, get_database
from schemas import UserResponse
from auth import router as auth_router   
import os
import uvicorn



app = FastAPI(title="User Authentication API")

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