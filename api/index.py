"""
Vercel serverless entrypoint (the official FastAPI-on-Vercel pattern).

Vercel's Python runtime serves the ASGI `app` exposed here. We reuse the exact
same FastAPI app from server.py, so one route table powers both local dev and
production. The /api/* rewrite in vercel.json sends API requests here; the
frontend in public/ is served separately by Vercel's CDN.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import app  # noqa: E402  (must follow the sys.path tweak)

# `app` is the ASGI application Vercel invokes.
