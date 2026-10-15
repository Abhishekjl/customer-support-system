# 🛍️ ShopEasy — Multi-Agent Customer Support System

A simple **multi-agent** customer support assistant for a fictional e-commerce
store. Built in Python using the **OpenAI (ChatGPT) API**. Designed to be easy
to read, run, and explain — great for a college project.

It also runs with **no API key** in a free offline **mock mode**, so it never
fails during a demo.

---

## 🧠 How it works (the multi-agent idea)

One customer message flows through two stages:

```
          Customer message
                 │
                 ▼
        ┌──────────────────┐
        │  🧭 Router Agent  │   decides the category
        └────────┬─────────┘
                 │  billing / technical / general
      ┌──────────┼──────────────┐
      ▼          ▼              ▼
 💳 Billing   🛠️ Technical    📦 General
   Agent        Agent          Agent
      └──────────┼──────────────┘
                 ▼
          Reply to customer
```

- **Router Agent** — reads the message and classifies it into `billing`,
  `technical`, or `general`.
- **Specialist Agents** — each has its own persona and is grounded in a small
  **knowledge base** (store FAQ/policies) so answers stay accurate.

Each agent is just an OpenAI call with a different system prompt — that's the
whole trick. No heavy frameworks.

---

## 📂 Project structure

| File | What it does |
|------|--------------|
| `main.py` | Terminal chat loop — the entry point. Shows the routing live. |
| `server.py` | FastAPI backend for **local** dev — serves the web UI + the JSON API. |
| `public/` | The browser front-end: `index.html` + `static/style.css` + `static/app.js` (plain HTML/CSS/JS). |
| `api/` | Vercel serverless functions (`status.py`, `chat.py`) — the API in production. |
| `agents.py` | The Router + Specialist agents (the core logic). |
| `knowledge_base.py` | The store's FAQ, used as AI context and for offline answers. |
| `llm.py` | One tidy wrapper around the OpenAI API (+ error handling). |
| `config.py` | Reads the API key / model and picks live vs mock mode. |
| `requirements.txt` | Dependencies (`openai`, `python-dotenv`, `fastapi`, `uvicorn`). |
| `.env.example` | Template for your API key. |

---

## 🚀 How to run this project (step by step)

### ✅ Step 0 — Prerequisites
You need **Python 3.8 or newer**. Check by running:
```bash
python3 --version
```
If you see a version number (e.g. `Python 3.12.2`), you're good. If not,
install Python from <https://www.python.org/downloads/>.

### 📁 Step 1 — Open a terminal in the project folder
```bash
cd path/to/multiagent-customer-support
```
(Use the folder where you saved the project.)

### 📦 Step 2 — Create a virtual environment
A "virtual environment" is a private folder that holds this project's packages,
so they don't clash with other Python projects on your computer.
```bash
python3 -m venv venv
```
This creates a `venv/` folder. You only do this **once**.

### 🔌 Step 3 — Activate the virtual environment
You do this **every time** you open a new terminal to work on the project.

- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```

When it's active, your terminal prompt shows `(venv)` at the start.

### ⬇️ Step 4 — Install the dependencies
```bash
pip install -r requirements.txt
```
This installs `openai`, `python-dotenv`, and — for the web UI — `fastapi` and
`uvicorn`. You only need to do this **once** per virtual environment.

### ▶️ Step 5 — Run the app
```bash
python main.py
```
Type a question (e.g. *"I want a refund"*), press Enter, and watch the Router
pick an agent. Type `quit` or `exit` to stop.

> 💡 **Shortcut (no activation needed):** instead of Steps 3 + 5 you can run the
> app directly with `./venv/bin/python main.py` (macOS/Linux).

### 🖥️ Step 5b (optional) — Run the web UI instead
Prefer a browser UI over the terminal? The project ships a **FastAPI** backend
plus a plain **HTML/CSS/JavaScript** front-end that drives the exact same Router
+ Specialist agents, with a chat box and a live "routing so far" panel.
```bash
python server.py
```
Then open <http://localhost:8000> in your browser. The sidebar shows whether
you're in **LIVE** or **MOCK** mode and tallies how many messages each
specialist handled.

> 💡 **How it's wired (local):** `server.py` exposes two endpoints — `GET /api/status`
> (live vs mock) and `POST /api/chat` (routes one message and returns the
> reply) — and serves the page in `public/`. The browser keeps the conversation
> and the routing tallies; the server stays stateless. On Vercel these two
> endpoints are the serverless functions in `api/` instead (same agent logic).
>
> You can also run it with uvicorn's auto-reload during development:
> `./venv/bin/uvicorn server:app --reload` (same URL). Interactive API docs are
> at <http://localhost:8000/docs>.

### 🛑 Step 6 — When you're done
Leave the virtual environment with:
```bash
deactivate
```

---

## 🔑 Choosing mock mode vs live AI

### Run for FREE with no key (mock mode)
Do nothing special — if there's no API key, the app uses built-in canned
answers. The banner shows **MOCK (offline, no API key)**. Great for a first test.

### Run with a real AI (live mode)
The code works with **any OpenAI-compatible provider** — you just set three
values in a `.env` file. The banner then shows **LIVE**.

**Easiest & free — Google Gemini:**
1. Get a free key at <https://aistudio.google.com/app/apikey>
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and set these three lines:
   ```ini
   OPENAI_API_KEY=your-gemini-key
   OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
   OPENAI_MODEL=gemini-flash-lite-latest
   ```
4. Run `python main.py` again — the banner now says **LIVE**.

> See `.env.example` for ready-made settings for **Gemini, OpenAI, Groq, and
> Ollama**. Switching provider = change those 3 lines, no code edits.
>
> **Free tiers have rate limits** (e.g. Gemini free tier allows only a handful
> of requests per minute). If you ask questions very quickly you may briefly hit
> the limit — the app just shows a short note and uses an offline answer, then
> recovers on the next question. It never crashes.

---

## ☁️ Deploy to Vercel

The web UI runs on Vercel as a **serverless function** — a perfect fit, since
the backend is stateless (the browser keeps the chat + tallies; the server just
routes one message at a time). Three files make this work:

| File | Role |
|------|------|
| `public/` | The front-end — served straight from Vercel's CDN (`/` and `/static/*`). |
| `api/status.py`, `api/chat.py` | One serverless function per endpoint — Vercel maps them to `/api/status` and `/api/chat` by filename (no rewrites needed). |
| `vercel.json` | Bundles the shared agent modules into the functions and sets a 30s timeout. |
| `.vercelignore` | Keeps `venv/`, caches, and `.env` out of the upload. |

### Option A — Deploy from GitHub (recommended)
1. Push this repo to GitHub.
2. Go to <https://vercel.com/new>, **Import** the repo. Vercel auto-detects the
   Python function — just click **Deploy**.
3. **Set the environment variables** (Project → Settings → Environment Variables),
   otherwise the live app falls back to MOCK answers:
   | Name | Value |
   |------|-------|
   | `OPENAI_API_KEY` | your Gemini (or other) key |
   | `OPENAI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
   | `OPENAI_MODEL` | `gemini-flash-lite-latest` |
4. **Redeploy** (Deployments → ⋯ → Redeploy) so the new variables take effect.

### Option B — Deploy from the CLI
```bash
npm i -g vercel      # one-time install
vercel               # first run links/creates the project
# add secrets (repeat for each, or set them in the dashboard):
vercel env add OPENAI_API_KEY
vercel env add OPENAI_BASE_URL
vercel env add OPENAI_MODEL
vercel --prod        # ship it
```

> ⚠️ **Never commit `.env`** — it's gitignored for a reason. On Vercel the key
> lives only in the Environment Variables settings. Without those variables the
> site still works, just in free offline **MOCK** mode.
>
> ⏱️ Each reply is a single model call, well within the 30s function limit set
> in `vercel.json` (`maxDuration`).

---

## 💬 Example session

```
You: I was charged twice for my order
   🧭 Router: classified as 'billing' -> handing off to Billing Agent
💳 Billing Agent: If you see a duplicate charge, it is usually a temporary
authorization hold that clears in 3-5 business days...

You: I can't log in
   🧭 Router: classified as 'technical' -> handing off to Technical Agent
🛠️ Technical Agent: If you can't log in, first try resetting your password...
```

---