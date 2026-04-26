from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

Category = Literal["billing", "technical", "refund"]


class Persona(BaseModel):
    id: int
    category: Category
    prompt_template: str
    updated_at: datetime
    updated_by_user_id: Optional[str] = None
    version: int


class PersonaUpdate(BaseModel):
    prompt_template: str = Field(min_length=50, max_length=10000)
