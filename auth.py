from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_database
from schemas import UserCreate, UserLogin, UserResponse, Token

from utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
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
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
        

    }
    
    
    # Insert into database
    result = await db.users.insert_one(user_doc)
    
    # Get the created user
    created_user = await db.users.find_one({"_id": result.inserted_id})
    
    return UserResponse(
        id=str(created_user["_id"]),
        name=created_user["name"],
        email=created_user["email"],
        created_at=created_user.get("created_at"),
        
        
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

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    """
    Get current logged in user information
    
    **Requires authentication token in header:**
    Authorization: Bearer <token>
    """
    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user.get("created_at")
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
