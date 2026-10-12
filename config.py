"""
Central configuration.

Reads settings from a .env file (if present) or the environment.
The single most important rule lives here:
    - If an OpenAI API key is found  -> use the real ChatGPT API ("live mode")
    - If no key is found             -> use free offline canned answers ("mock mode")
This is what lets the project run for anyone, even with no key and no internet.
"""

import os

# python-dotenv is optional. If it's not installed we just skip loading .env
# so the program never crashes on a missing package.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Optional: point at any OpenAI-COMPATIBLE provider (Google Gemini, Groq,
# OpenRouter, Ollama...) by setting OPENAI_BASE_URL in .env.
# Blank = use real OpenAI.
BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None

# No key => mock mode. This is checked everywhere instead of re-reading the key.
USE_MOCK = not bool(OPENAI_API_KEY)
