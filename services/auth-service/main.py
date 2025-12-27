"""Authentication Service - Handles JWT authentication and user management"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext
from shared.common import setup_logger, get_config, HealthResponse
from shared.common.db_client import get_db_client
import secrets

# Setup logger
logger = setup_logger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI app
app = FastAPI(
    title="Authentication Service",
    description="JWT authentication and user management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="auth-service",
        version="1.0.0"
    )


@app.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register new user"""
    db = get_db_client()
    
    # Check if user exists
    existing = db.execute_query(
        "SELECT * FROM users WHERE username = %s OR email = %s",
        (user.username, user.email)
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db.execute_update(
        "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
        (user.username, user.email, hashed_password)
    )
    
    return User(username=user.username, email=user.email)


@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login and get JWT token"""
    db = get_db_client()
    
    # Get user
    users = db.execute_query(
        "SELECT * FROM users WHERE username = %s",
        (user.username,)
    )
    
    if not users or not verify_password(user.password, users[0]["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/me", response_model=User)
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current user info"""
    username = payload.get("sub")
    db = get_db_client()
    
    users = db.execute_query(
        "SELECT username, email FROM users WHERE username = %s",
        (username,)
    )
    
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(username=users[0]["username"], email=users[0]["email"])


@app.get("/verify")
async def verify_token_endpoint(payload: dict = Depends(verify_token)):
    """Verify token validity"""
    return {"valid": True, "username": payload.get("sub")}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

