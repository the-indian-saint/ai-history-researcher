"""Authentication routes for user management (not yet integrated).

This module contains authentication functionality for future use.
Currently, the application runs without authentication requirements.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

# NOTE: Authentication is implemented but not enforced in the application.
# To enable authentication in the future:
# 1. Create a users table in the database
# 2. Add JWT dependencies (python-jose[cryptography], passlib[bcrypt])
# 3. Configure JWT settings in config.py
# 4. Apply get_current_user dependency to protected routes


class UserCreate(BaseModel):
    """User creation request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    user_id: Optional[str] = None


# Uncomment and configure when ready to use authentication
"""
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import text
from ...config import settings
from ...storage.database import get_database
from ...utils.logging import get_logger

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if username is None:
            raise credentials_exception
        
        return TokenData(username=username, user_id=user_id)
        
    except JWTError:
        raise credentials_exception


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        async with get_database() as db:
            # Check if user exists
            result = await db.execute(
                text("SELECT id FROM users WHERE username = :username OR email = :email"),
                {"username": user.username, "email": user.email}
            )
            if result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )
            
            # Create new user
            hashed_password = get_password_hash(user.password)
            result = await db.execute(
                text('''INSERT INTO users (username, email, password_hash, full_name, is_active, created_at)
                    VALUES (:username, :email, :password_hash, :full_name, true, :created_at)
                    RETURNING id, username, email, full_name, is_active, created_at'''),
                {
                    "username": user.username,
                    "email": user.email,
                    "password_hash": hashed_password,
                    "full_name": user.full_name,
                    "created_at": datetime.utcnow()
                }
            )
            await db.commit()
            new_user = result.fetchone()
            
            logger.info(f"New user registered: {user.username}")
            
            return UserResponse(
                id=str(new_user.id),
                username=new_user.username,
                email=new_user.email,
                full_name=new_user.full_name,
                is_active=new_user.is_active,
                created_at=new_user.created_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        async with get_database() as db:
            result = await db.execute(
                text("SELECT id, username, password_hash FROM users WHERE username = :username AND is_active = true"),
                {"username": form_data.username}
            )
            user = result.fetchone()
            
            if not user or not verify_password(form_data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
            access_token = create_access_token(
                data={"sub": user.username, "user_id": str(user.id)},
                expires_delta=access_token_expires
            )
            
            logger.info(f"User logged in: {user.username}")
            
            return Token(
                access_token=access_token,
                expires_in=settings.jwt_expire_minutes * 60
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    try:
        async with get_database() as db:
            result = await db.execute(
                text("SELECT * FROM users WHERE id = :user_id"),
                {"user_id": current_user.user_id}
            )
            user = result.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return UserResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
"""
