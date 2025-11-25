from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
from datetime import date


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration"""

    name: str = Field(..., min_length=2, max_length=50, description="User's full name", example= "John Doe")
    email: EmailStr = Field(..., description="User's email address", example ="john@gmail.com")
    password: Optional[str] = Field(..., min_length=1, description="User's password (min 6 characters)", example= "securepass123")

    #Fields for streak and reward points
    streak: int=0
    xp: int =0
    total_checkins: int=0
    last_checkin: Optional[date] = None

    # NEW — Mode system
    mode: Optional[str]= None        # "casual" or "locked_in"
    last_coding_date: Optional[str] = None
    missed_days: int = 0
    penalty_remaining: int = 0
    weekly_reset_date: Optional[str] = None

    # Locked in session fields
    locked_in_active: bool = False
    locked_in_problems_required: int = 0
    locked_in_problems_completed: int = 0
    locked_in_started_at: Optional[str] = None
    locked_in_time_limit: int = 0


    #for examples in swaggers ui docs
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepass123"
            }
        }

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address", example ="john@gmail.com")
    password: str = Field(..., min_length=1, description="User's password", example= "securepass123")
  

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepass123"
            }
        }

class UserResponse(BaseModel):

    """Schema for user response (without password)"""

    id: str = Field(..., description="User's unique identifier", example="507f1f77bcf86cd799439011")
    name: str = Field(..., description="User's full name", example= "John Doe")
    email: str = Field(..., description="User's email", example= "John@gmail.com")
    created_at: str= Field(..., description="Account creation timestamp", example="2024-01-15T10:30:00")

    #fields for streak and reward points for front end display
    streak: int =0
    xp: int =0
    total_checkins: int=0
    last_checkin: Optional[date]= None

    # NEW — Mode system
    mode: str ="casual" or "locked_in"
    last_coding_date: Optional[str] = None
    missed_days: int = 0
    penalty_remaining: int = 0
    weekly_reset_date: Optional[str] = None

    # Locked in session fields
    locked_in_active: bool = False
    locked_in_problems_required: int = 0
    locked_in_problems_completed: int = 0
    locked_in_started_at: Optional[str] = None
    locked_in_time_limit: int = 0



    class Config:

        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class UserInDB(BaseModel):
    """Schema for user in database"""
    id: str = Field(default=None, alias="_id")
    name: str
    email: str
    hashed_password: Optional[str]
    provider: str = "manual"  #manual for user and google for google
    created_at: str

    #new fields for xps and streaks
    streak: int = 0
    xp: int =0
    total_checkins: int=0
    last_active_date: Optional[date] = None

    # NEW — Mode system
    mode: str = "casual"           # "casual" or "locked_in"
    last_coding_date: Optional[str] = None
    missed_days: int = 0
    penalty_remaining: int = 0
    weekly_reset_date: Optional[str] = None

    # Locked in session fields
    locked_in_active: bool = False
    locked_in_problems_required: int = 0
    locked_in_problems_completed: int = 0
    locked_in_started_at: Optional[str] = None
    locked_in_time_limit: int = 0


    class Config:
        populate_by_name = True


# Token Schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str


    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }



class TokenData(BaseModel):
    """Schema for token payload data"""
    email: Optional[str] = None

class ChatLog(BaseModel):
    """Schema for chat log entries"""
    user_id: str
    role: str  # "user" or "assistant"
    message: str
    timestamp: datetime