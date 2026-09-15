from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ---------- Base ----------
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


# ---------- Request schemas ----------
class UserCreate(UserBase):
    """Used for registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Used for login"""
    email: EmailStr
    password: str


# ---------- Response schemas ----------
class UserResponse(UserBase):
    """What we return to the client (never includes password)"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Returned after successful login"""
    access_token: str
    token_type: str = "bearer"