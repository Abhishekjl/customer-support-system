"""
Vercel serverless function  ->  GET /api/status

Vercel maps this file to the path /api/status automatically (filesystem
routing), so there are no rewrites or ASGI path tricks to get wrong. It tells
the UI whether we're on the real AI (LIVE) or the offline fallback (MOCK).

The actual logic lives in the shared modules (llm.py, config.py) — exactly the
same ones the terminal app and the local FastAPI server use.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Make the project-root modules importable from inside api/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import llm                       # noqa: E402
from config import MODEL         # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        live = llm.is_live()
        payload = {
            "live": live,
            "mode": "LIVE" if live else "MOCK",
            "model": MODEL if live else "offline canned answers",
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
