"""
Security middleware: input validation, rate limiting, security headers.
"""
import os
import re
import time
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Rate limiting state: {ip_address: [timestamps]}
_rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_SKIP_PATHS = {"/health", "/docs", "/openapi.json"}


def get_client_ip(request: Request) -> str:
    """Extract client IP, handling proxies."""
    if forwarded := request.headers.get("X-Forwarded-For"):
        return forwarded.split(",")[0].strip()
    if client := request.client:
        return client.host
    return "unknown"


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware. Allows graceful degradation."""
    if request.url.path in RATE_LIMIT_SKIP_PATHS or request.method == "OPTIONS":
        return await call_next(request)

    client_ip = get_client_ip(request)
    now = time.time()

    # Cleanup old entries
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip] if now - ts < RATE_LIMIT_WINDOW
    ]

    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(
            f"Rate limit exceeded for IP {client_ip}",
            extra={"client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    _rate_limit_store[client_ip].append(now)
    return await call_next(request)


async def add_security_headers(request: Request, call_next: Callable) -> Response:
    """Add security headers to response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    return response


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize string input: remove HTML, limit length."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")
    
    # Remove common HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
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


def validate_password(password: str) -> None:
    """Validate password strength."""
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")
    
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a digit")
