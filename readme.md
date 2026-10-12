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
| `agents.py` | The Router + Specialist agents (the core logic). |
| `knowledge_base.py` | The store's FAQ, used as AI context and for offline answers. |
| `llm.py` | One tidy wrapper around the OpenAI API (+ error handling). |
| `config.py` | Reads the API key / model and picks live vs mock mode. |
| `requirements.txt` | Dependencies (`openai`, `python-dotenv`). |
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
This installs the two packages the project needs: `openai` and `python-dotenv`.
You only need to do this **once** per virtual environment.

### ▶️ Step 5 — Run the app
```bash
python main.py
```
Type a question (e.g. *"I want a refund"*), press Enter, and watch the Router
pick an agent. Type `quit` or `exit` to stop.

> 💡 **Shortcut (no activation needed):** instead of Steps 3 + 5 you can run the
> app directly with `./venv/bin/python main.py` (macOS/Linux).

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