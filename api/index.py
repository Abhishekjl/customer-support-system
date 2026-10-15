"""
Vercel serverless entrypoint.

Vercel's Python runtime looks for an ASGI app named `app` in this file and
serves it. We reuse the EXACT same FastAPI app from server.py — so the route
table that powers local `python server.py` also powers the deployment. There's
no second copy of the logic to keep in sync.

The sys.path line makes the project-root modules (server.py, agents.py, llm.py,
config.py, knowledge_base.py) importable from inside this api/ folder.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import app  # noqa: E402  (must come after the sys.path tweak)

# `app` is what Vercel serves. Nothing else to do here.
