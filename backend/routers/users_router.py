import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..db import UserModel, AuditLogModel, get_session
from ..auth import hash_password, require_admin
from ..schemas.user import User, UserCreate
from ..security import validate_email, validate_password

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


def _row_to_user(u: UserModel) -> User:
    return User(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        role=u.role,
        assigned_category=u.assigned_category,
        is_active=u.is_active,
        created_at=u.created_at,
        last_login_at=u.last_login_at,
    )


@router.get("", response_model=list[User])
def list_users(
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
):
    session = get_session()
    try:
        q = session.query(UserModel)
        if role:
            q = q.filter(UserModel.role == role)
        return [_row_to_user(u) for u in q.order_by(UserModel.created_at).all()]
    finally:
        session.close()


@router.post("", response_model=User, status_code=201)
def create_user(
    body: UserCreate,
    current_user: User = Depends(require_admin),
):
    # Validate email
    if not validate_email(body.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate password
    validate_password(body.password)
    
    session = get_session()
    try:
        if session.query(UserModel).filter_by(email=body.email).first():
            logger.warning(f"Attempt to create user with existing email: {body.email}")
            raise HTTPException(status_code=409, detail="Email already registered")

        new_user = UserModel(
            id=f"user-{uuid.uuid4().hex[:12]}",
            email=body.email,
            full_name=body.full_name,
            password_hash=hash_password(body.password),
            role=body.role,
            assigned_category=body.assigned_category,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        session.add(new_user)
        session.add(AuditLogModel(
            user_id=current_user.id,
            action="user_create",
            target_type="user",
            target_id=new_user.id,
        ))
        session.commit()
        
        logger.info(f"User created: {new_user.id} ({body.email}) by {current_user.id}")
        
        return _row_to_user(new_user)
    finally:
        session.close()


@router.patch("/{user_id}", response_model=User)
def update_user(
    user_id: str,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    current_user: User = Depends(require_admin),
):
    session = get_session()
    try:
        u = session.query(UserModel).filter_by(id=user_id).first()
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot modify your own account")

        if is_active is not None:
            u.is_active = is_active
        if role is not None:
            u.role = role
        session.commit()
        return _row_to_user(u)
    finally:
        session.close()
