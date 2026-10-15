"""
Vercel serverless function  ->  POST /api/chat

Vercel maps this file to the path /api/chat automatically. It runs one customer
message through the full multi-agent pipeline (Router -> Specialist) and returns
the reply as JSON — the identical two-step flow used everywhere else, just
reusing ROUTER and SPECIALISTS from agents.py.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Make the project-root modules importable from inside api/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import ROUTER, SPECIALISTS   # noqa: E402

ICONS = {"billing": "💳", "technical": "🛠️", "general": "📦"}


def route_and_answer(message):
    """Route one message, then let the matching specialist answer."""
    message = (message or "").strip()
    if not message:
        general = SPECIALISTS["general"]
        return {
            "category": "general",
            "agent_name": general.name,
            "icon": ICONS["general"],
            "reply": "Please type a question and I'll route it to the right specialist. 🙂",
        }
    category = ROUTER.route(message)
    agent = SPECIALISTS[category]
    return {
        "category": category,
        "agent_name": agent.name,
        "icon": ICONS[category],
        "reply": agent.handle(message),
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            message = json.loads(raw.decode("utf-8")).get("message", "")
        except (ValueError, AttributeError):
            message = ""

        payload = route_and_answer(message)
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
