from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime

Role = Literal["specialist", "senior", "admin"]
Category = Literal["billing", "technical", "refund"]


class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: Role
    assigned_category: Optional[Category] = None
    is_active: bool = True
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=100)
    role: Role
    assigned_category: Optional[Category] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
