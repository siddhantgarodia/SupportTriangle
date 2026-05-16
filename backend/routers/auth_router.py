from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from db import UserModel, AuditLogModel, get_session
from auth import verify_password, create_access_token, get_current_user, hash_password
from schemas.user import User, UserCreate, TokenResponse
from security import validate_email, validate_password

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    session = get_session()
    try:
        user = session.query(UserModel).filter_by(email=form_data.username, is_active=True).first()
        if not user or not verify_password(form_data.password, user.password_hash):
            logger.warning(f"Failed login attempt for {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user.last_login_at = datetime.utcnow()
        session.add(AuditLogModel(
            user_id=user.id,
            action="login",
            target_type="user",
            target_id=user.id,
        ))
        session.commit()
        
        logger.info(f"User logged in: {user.id} ({user.email})")
        
        token = create_access_token(user.id, user.role, user.assigned_category)
        return TokenResponse(
            access_token=token,
            user=User(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                assigned_category=user.assigned_category,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            ),
        )
    finally:
        session.close()


@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)):
    return current_user
