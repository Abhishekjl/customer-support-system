"""
Thin wrapper around the OpenAI (ChatGPT) API.

Everything that talks to the AI goes through chat() below. This keeps the
agent code clean and gives us ONE place to handle errors and mock mode.

Design choice: chat() returns a string on success, or None on any failure
(no key, no internet, API error, package missing). When the caller gets None,
it falls back to an offline canned answer. That's why the demo can never crash.
"""

from config import OPENAI_API_KEY, MODEL, USE_MOCK, BASE_URL

# Create the OpenAI client once, and only if we actually have a key.
_client = None
if not USE_MOCK:
    try:
        from openai import OpenAI
        # base_url lets us talk to Gemini/Groq/etc. If None, uses real OpenAI.
        _client = OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)
    except Exception as exc:  # package not installed, bad key format, etc.
        print(f"[llm] Could not start OpenAI client ({exc}). Using mock mode.")
        _client = None


def is_live():
    """True if we are really calling the OpenAI API, False if offline/mock."""
    return _client is not None


def _short_reason(exc):
    """Turn a big ugly API exception into a short, friendly one-line reason."""
    code = getattr(exc, "status_code", None)
    if code == 429:
        return "free-tier rate limit hit — wait ~1 min"
    if code in (401, 403):
        return "API key rejected"
    if code == 404:
        return "model name not found"
    text = str(exc)
    return text[:80] + ("..." if len(text) > 80 else "")


def chat(system_prompt, user_message, temperature=0.3):
    """
    Ask the model one question with a given 'role' (system_prompt).

    Returns the model's text reply, or None if we couldn't get one
    (so the caller can use an offline fallback instead).
    """
    if _client is None:
        return None
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        # Network issue, rate limit, invalid key... never crash the app.
        print(f"   [info] Live API unavailable ({_short_reason(exc)}); "
              f"using offline answer.")
        return None
