"""
ShopEasy — Multi-Agent Customer Support  ·  FastAPI backend
Run:  uvicorn server:app --reload     (or:  python server.py)

This is a web front-end for the SAME multi-agent engine that powers main.py.
Nothing about the agents changes — we just reuse ROUTER and SPECIALISTS and
expose them over a tiny JSON API, then serve a plain HTML/CSS/JS page that
talks to it. The browser keeps the conversation + routing tallies; the server
stays stateless, so one message in = one routed reply out.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import llm
from agents import ROUTER, SPECIALISTS
from config import MODEL

# Same icons as the terminal app, so the two front-ends feel like one product.
ICONS = {
    "Router": "🧭",
    "billing": "💳",
    "technical": "🛠️",
    "general": "📦",
}

# The browser front-end lives in public/ so that BOTH this local server and
# Vercel serve it the same way (on Vercel, public/ is served straight from the
# CDN; here we serve it ourselves). index.html references /static/... which maps
# to public/static/... in both places.
PUBLIC_DIR = Path(__file__).parent / "public"

app = FastAPI(title="ShopEasy — Multi-Agent Support")


# ---------------------------------------------------------------------------
# Request / response shapes (pydantic gives us validation + clean docs)
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    category: str
    agent_name: str
    icon: str
    reply: str


class StatusResponse(BaseModel):
    live: bool
    mode: str
    model: str


# ---------------------------------------------------------------------------
# Core pipeline — identical two-step flow to handle_message() in main.py
# ---------------------------------------------------------------------------
def run_pipeline(message):
    """Route one message, then let the matching specialist answer."""
    category = ROUTER.route(message)
    agent = SPECIALISTS[category]
    reply = agent.handle(message)
    return category, agent.name, reply


# ---------------------------------------------------------------------------
# Endpoint logic (shared by the typed routes and the Vercel shim below)
# ---------------------------------------------------------------------------
def _status_payload():
    """Whether we're on the real AI (LIVE) or offline (MOCK)."""
    live = llm.is_live()
    return {
        "live": live,
        "mode": "LIVE" if live else "MOCK",
        "model": MODEL if live else "offline canned answers",
    }


def _chat_payload(message):
    """Run one customer message through the full multi-agent pipeline."""
    message = (message or "").strip()
    if not message:
        # An empty message just gets a gentle nudge rather than an error.
        return {
            "category": "general",
            "agent_name": SPECIALISTS["general"].name,
            "icon": ICONS["general"],
            "reply": "Please type a question and I'll route it to the right specialist. 🙂",
        }
    category, agent_name, reply = run_pipeline(message)
    return {
        "category": category,
        "agent_name": agent_name,
        "icon": ICONS[category],
        "reply": reply,
    }


# ---------------------------------------------------------------------------
# API routes (used locally, and on Vercel when the real path is preserved)
# ---------------------------------------------------------------------------
@app.get("/api/status", response_model=StatusResponse)
def status():
    return StatusResponse(**_status_payload())


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return ChatResponse(**_chat_payload(req.message))


# ---------------------------------------------------------------------------
# Serve the web UI
#
# These two routes exist for LOCAL dev (`python server.py`). On Vercel the
# frontend in public/ is served straight from the CDN and never reaches this
# app, so the public/ folder isn't bundled into the serverless function — which
# is why both are guarded: importing this module must never crash just because
# public/ is absent (that was the FUNCTION_INVOCATION_FAILED on Vercel).
# ---------------------------------------------------------------------------
_INDEX_FILE = PUBLIC_DIR / "index.html"
_STATIC_DIR = PUBLIC_DIR / "static"


@app.get("/")
def index():
    """Serve the single-page app (local dev); on Vercel the CDN handles this."""
    if _INDEX_FILE.is_file():
        return FileResponse(_INDEX_FILE)
    return {"status": "ok", "note": "API is up; frontend is served by the CDN."}


if _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Vercel path shim — registered LAST so it only catches what nothing else did.
#
# Vercel's "/api/(.*) -> /api/index" rewrite hands this app the *destination*
# path (/api/index) instead of the original (/api/status | /api/chat), which
# collapses both endpoints onto one path and 404s the typed routes above. Our
# two API endpoints use distinct HTTP methods, so we dispatch by method here and
# the app works regardless of which path Vercel passes through. Locally the
# typed routes match first and this never runs.
# ---------------------------------------------------------------------------
@app.api_route("/{_catch_all:path}", methods=["GET", "POST"])
async def _vercel_shim(_catch_all: str, request: Request):
    if request.method == "GET":
        return JSONResponse(_status_payload())
    try:
        data = await request.json()
    except Exception:
        data = {}
    message = data.get("message", "") if isinstance(data, dict) else ""
    return JSONResponse(_chat_payload(message))


if __name__ == "__main__":
    # Convenience: `python server.py` works too, not only `uvicorn server:app`.
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
