from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from ..db import PersonaModel, AuditLogModel, get_session
from ..auth import get_current_user, require_senior_or_above
from ..schemas.user import User
from ..schemas.persona import Persona, PersonaUpdate

router = APIRouter(prefix="/personas", tags=["personas"])


def _row_to_persona(p: PersonaModel) -> Persona:
    return Persona(
        id=p.id,
        category=p.category,
        prompt_template=p.prompt_template,
        updated_at=p.updated_at,
        updated_by_user_id=p.updated_by_user_id,
        version=p.version,
    )


@router.get("", response_model=list[Persona])
def list_personas(current_user: User = Depends(require_senior_or_above)):
    session = get_session()
    try:
        personas = session.query(PersonaModel).order_by(PersonaModel.category).all()
        return [_row_to_persona(p) for p in personas]
    finally:
        session.close()


@router.get("/{category}", response_model=Persona)
def get_persona(category: str, current_user: User = Depends(require_senior_or_above)):
    session = get_session()
    try:
        p = session.query(PersonaModel).filter_by(category=category).first()
        if not p:
            raise HTTPException(status_code=404, detail=f"Persona not found for category '{category}'")
        return _row_to_persona(p)
    finally:
        session.close()


@router.put("/{category}", response_model=Persona)
def update_persona(
    category: str,
    body: PersonaUpdate,
    current_user: User = Depends(require_senior_or_above),
):
    session = get_session()
    try:
        p = session.query(PersonaModel).filter_by(category=category).first()
        if not p:
            raise HTTPException(status_code=404, detail=f"Persona not found for category '{category}'")

        p.prompt_template = body.prompt_template
        p.updated_at = datetime.utcnow()
        p.updated_by_user_id = current_user.id
        p.version += 1

        session.add(AuditLogModel(
            user_id=current_user.id,
            action="persona_edit",
            target_type="persona",
            target_id=category,
            metadata_json=None,
        ))
        session.commit()
        return _row_to_persona(p)
    finally:
        session.close()
