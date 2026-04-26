"""
Vercel serverless entry point for the FastAPI backend.
Strips the /api prefix before passing requests to FastAPI,
so FastAPI route definitions stay clean (e.g. /tickets not /api/tickets).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app as _app


class _StripApiPrefix:
    """ASGI middleware: strip /api prefix added by Vercel's rewrite rules."""

    def __init__(self, app, prefix: str = "/api"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path: str = scope.get("path", "/")
            if path.startswith(self.prefix):
                stripped = path[len(self.prefix):] or "/"
                scope = {**scope, "path": stripped}
                raw: bytes = scope.get("raw_path", path.encode())
                prefix_bytes = self.prefix.encode()
                if raw.startswith(prefix_bytes):
                    scope["raw_path"] = raw[len(prefix_bytes):] or b"/"
        await self.app(scope, receive, send)


app = _StripApiPrefix(_app)
