"""
Security: input validation and sanitization.
"""
import re
from fastapi import HTTPException
from email_validator import validate_email as _ev_validate, EmailNotValidError


def validate_email(email: str) -> bool:
    """Validate email format using the email-validator library."""
    try:
        _ev_validate(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize string input: remove HTML tags and dangerous URI schemes, limit length."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Strip dangerous URI schemes (javascript:, data:, vbscript:)
    text = re.sub(r"(?i)(javascript|data|vbscript):", "", text)

    return text.strip()


def validate_ticket_input(customer_name: str, email: str, subject: str, message: str) -> None:
    """Validate ticket creation input."""
    if not customer_name or not customer_name.strip():
        raise HTTPException(status_code=400, detail="customer_name is required")

    if len(customer_name) > 100:
        raise HTTPException(status_code=400, detail="customer_name is too long (max 100 chars)")

    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if not subject or not subject.strip():
        raise HTTPException(status_code=400, detail="subject is required")

    if len(subject) > 200:
        raise HTTPException(status_code=400, detail="subject is too long (max 200 chars)")

    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    if len(message) > 10000:
        raise HTTPException(status_code=400, detail="message is too long (max 10,000 chars)")


_SPECIAL_CHARS = set('!@#$%^&*()_+-=[]{}|;:,.<>?')


def validate_password(password: str) -> None:
    """Validate password strength."""
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")

    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a digit")

    if not any(c in _SPECIAL_CHARS for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a special character (!@#$%^&* etc.)")
