from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, date
from database import get_database
from schemas import UserCreate, UserLogin, UserResponse, Token
from utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from locked_in import update_locked_in_status
import os



# Create router for auth endpoints
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# OAuth2 scheme - token will be taken from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# ============================================
# HELPER FUNCTIONS
# ============================================

async def authenticate_user(email: str, password: str, db) -> dict | bool:
    """
    Authenticate a user by email and password
    
    Args:
        email: User's email
        password: User's plain password
        db: Database instance
        
    Returns:
        dict: User document if authenticated, False otherwise
    """
    user = await db.users.find_one({"email": email})
    
    if not user:
        return False
    
    if not verify_password(password, user["hashed_password"]):
        return False
    
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_database)
) -> dict:
    """
    Get current user from JWT token
    
    Args:
        token: JWT token from Authorization header
        db: Database instance
        
    Returns:
        dict: Current user document
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await db.users.find_one({"email": email})
    
    if user is None:
        raise credentials_exception
    
    return user

# ============================================
# ROUTES
# ============================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db = Depends(get_database)):
    """
    Register a new user
    
    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 6 characters)
    """
    print(f"Connected to database: {db.name}")
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email already registered {db.name} database"

        )
    
    # Hash the password
    try:
        if len(user.password.encode("utf-8")) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too long (max 72 characters)"
            )
        hashed_password = get_password_hash(user.password)
        print(hashed_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f" band baj gyi Password hashing failed: {str(e)}",
            
        )
    
    # Create user document
    user_doc = {
        "_id": user.email,
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),

        "streak": 0,
        "xp": 0,
        "total_checkins": 0,
        "last_active_date": None,
        "last_login_date": None,

        # Locked-in mode defaults
        "mode": "casual",
        "last_coding_date": None,
        "missed_days": 0,
        "penalty_remaining": 0,
        "weekly_reset_date": None,

        # Locked in session fields
        "locked_in_active": False,
        "locked_in_problems_required": 0,
        "locked_in_problems_completed": 0,
        "locked_in_started_at": None,
        "locked_in_time_limit": 0




    }
    
    
    # Insert into database
    result = await db.users.insert_one(user_doc)
    
    # Get the created user
    created_user = await db.users.find_one({"_id": result.inserted_id})
    
    return UserResponse(
        id=created_user["_id"],
        name=created_user["name"],
        email=created_user["email"],
        created_at=created_user.get("created_at"),
        
        # NEW FIELDS
        streak=created_user.get("streak", 0),
        xp=created_user.get("xp", 0),
        total_checkins=created_user.get("total_checkins", 0),
        last_active_date=created_user.get("last_active_date")
    )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_database)
):
    """
    Login with email and password to get access token (Form data - for Swagger UI)
    
    - **username**: User's email (use email here)
    - **password**: User's password
    """
    
    # Authenticate user (form_data.username contains email)
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login_json(user_login: UserLogin, db = Depends(get_database)):
    """
    Login with JSON body to get access token (easier for API calls)
    
    - **email**: User's email
    - **password**: User's password
    """
    
    # Authenticate user
    user = await authenticate_user(user_login.email, user_login.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    await update_locked_in_status(db, user)
    # ---------------------------------------
    # DAILY LOGIN XP LOGIC
    # ---------------------------------------
    from datetime import date, datetime
    
    today = date.today()
    last_login_iso = user.get("last_login_date")
    last_login_date = None

    if last_login_iso:
        last_login_date = datetime.fromisoformat(last_login_iso).date()

    # Only reward XP if user hasn't logged in today
    if last_login_date != today:
        await db.users.update_one(
            {"email": user_login.email},
            {
                "$inc": {"xp": 20},  # Reward 20 XP
                "$set": {"last_login_date": today.isoformat()}
            }
        )
        print("⭐ Daily login bonus applied: +20 XP")
    else:
        print("Daily login already counted. No XP this time.")

    
    # Create JWT access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user["name"],
        "mode": user.get("mode"),
        "streak": user.get("streak", 0),
        "xp": user.get("xp", 0),
        "penalty_remaining": user.get("penalty_remaining", 0)


    }

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: dict = Depends(get_current_user),
                            db=Depends(get_database)):
    """
    Get current logged in user information
    
    **Requires authentication token in header:**
    Authorization: Bearer <token>
    """

    # Run daily locked-in status updater (no-op if not in locked_in mode)
    updated_user = await update_locked_in_status(db, user=current_user)

    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user.get("created_at"),
        streak=updated_user.get("streak", 0),
        xp=updated_user.get("xp", 0),
        total_checkins=updated_user.get("total_checkins", 0),
        last_active_date=updated_user.get("last_active_date"),
        mode=updated_user.get("mode"),
        last_coding_date=updated_user.get("last_coding_date"),
        penalty_remaining=updated_user.get("penalty_remaining", 0),
        missed_days=updated_user.get("missed_days", 0)
        


    )

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """
    Example of a protected route that requires authentication
    """
    return {
        "message": f"Hello {current_user['name']}! This is a protected route.",
        "user_email": current_user["email"],
        "access_level": "authenticated"
    }

@router.get("/debug/show-users")
async def show_users(db = Depends(get_database)):
    users = await db.users.find().to_list(10)
    for user in users:
        user["_id"] = str(user["_id"])
    print("Users in DB:", users)
    return users


@router.post("/mode")
async def update_mode(mode: str,
                      db=Depends(get_database),
                      current_user=Depends(get_current_user)):

    if mode not in ["casual", "locked_in"]:
        raise HTTPException(status_code=400, detail="Invalid mode.")

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"mode": mode}}
    )

    return {"message": f"Mode switched to {mode}."}

@router.get("/chat/logs")
async def get_chat_logs(db=Depends(get_database),
                        current_user=Depends(get_current_user)):
    logs = await db.chat_logs.find({"user_id": current_user["_id"]}) \
                             .sort("timestamp", 1) \
                             .to_list(length=500)

    # Convert ObjectId to string for JSON serialization
    for log in logs:
        log["_id"] = str(log["_id"])
        log["user_id"] = str(log["user_id"])
    
    return logs


