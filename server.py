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

from fastapi import FastAPI
from fastapi.responses import FileResponse
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
# API routes
# ---------------------------------------------------------------------------
@app.get("/api/status", response_model=StatusResponse)
def status():
    """Tell the UI whether we're on the real AI (LIVE) or offline (MOCK)."""
    live = llm.is_live()
    return StatusResponse(
        live=live,
        mode="LIVE" if live else "MOCK",
        model=MODEL if live else "offline canned answers",
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Run one customer message through the full multi-agent pipeline."""
    message = req.message.strip()
    if not message:
        # Keep the contract simple: an empty message just gets a gentle nudge
        # from the general agent rather than an error the UI has to handle.
        return ChatResponse(
            category="general",
            agent_name=SPECIALISTS["general"].name,
            icon=ICONS["general"],
            reply="Please type a question and I'll route it to the right specialist. 🙂",
        )

    category, agent_name, reply = run_pipeline(message)
    return ChatResponse(
        category=category,
        agent_name=agent_name,
        icon=ICONS[category],
        reply=reply,
    )


# ---------------------------------------------------------------------------
# Serve the web UI
# ---------------------------------------------------------------------------
@app.get("/")
def index():
    """Serve the single-page app."""
    return FileResponse(PUBLIC_DIR / "index.html")


# Everything else (style.css, app.js, …) is served as static files.
app.mount("/static", StaticFiles(directory=PUBLIC_DIR / "static"), name="static")


if __name__ == "__main__":
    # Convenience: `python server.py` works too, not only `uvicorn server:app`.
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
