"""
Authentication and authorization layer.
- Password hashing via pbkdf2_sha256 (passlib)
- JWT issuance and validation (PyJWT)
- FastAPI dependencies for current_user and role guards
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_MINUTES
from .db import UserModel, get_session
from .schemas.user import User, Role

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(user_id: str, role: str, assigned_category: Optional[str]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "assigned_category": assigned_category,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: no subject")

    session = get_session()
    try:
        user_row = session.query(UserModel).filter_by(id=user_id, is_active=True).first()
        if not user_row:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return User(
            id=user_row.id,
            email=user_row.email,
            full_name=user_row.full_name,
            role=user_row.role,
            assigned_category=user_row.assigned_category,
            is_active=user_row.is_active,
            created_at=user_row.created_at,
            last_login_at=user_row.last_login_at,
        )
    finally:
        session.close()


def require_role(*allowed_roles: Role):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.role}' not authorized; requires one of {allowed_roles}",
            )
        return current_user
    return checker


require_specialist_or_above = require_role("specialist", "senior", "admin")
require_senior_or_above = require_role("senior", "admin")
require_admin = require_role("admin")
