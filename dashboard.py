"""
ShopEasy — Multi-Agent Customer Support  ·  Streamlit dashboard
Run:  streamlit run dashboard.py

This is a visual front-end for the SAME multi-agent engine that powers
main.py. Nothing about the agents changes — we just reuse ROUTER and
SPECIALISTS and show the flow (Router -> Specialist) in a browser, plus a
little live analytics panel so you can watch the routing happen.
"""

import streamlit as st

import llm
from agents import ROUTER, SPECIALISTS

# Same icons as the terminal app, so the two front-ends feel like one product.
ICONS = {
    "Router": "🧭",
    "billing": "💳",
    "technical": "🛠️",
    "general": "📦",
}

# A few one-click examples so a first-time visitor can see the routing instantly.
EXAMPLES = [
    "I was charged twice for my order",
    "I forgot my password and can't log in",
    "Where is my order? It hasn't arrived yet",
    "How do I cancel my ShopEasy Plus membership?",
]


# ---------------------------------------------------------------------------
# Page + session setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ShopEasy — Multi-Agent Support",
    page_icon="🛍️",
    layout="wide",
)

# Conversation history + running tallies live in the session so they survive
# Streamlit's re-run-on-every-interaction model.
if "messages" not in st.session_state:
    # Each item: {"role", "content", and for assistant turns also "category"}.
    st.session_state.messages = []
if "counts" not in st.session_state:
    st.session_state.counts = {"billing": 0, "technical": 0, "general": 0}


def run_pipeline(message):
    """Route one message, then let the matching specialist answer.

    Returns (category, agent_name, reply) — the exact same two-step flow as
    handle_message() in main.py, just without printing to a terminal.
    """
    category = ROUTER.route(message)
    agent = SPECIALISTS[category]
    reply = agent.handle(message)
    return category, agent.name, reply


def handle_user_message(message):
    """Append the user's turn, run the pipeline, and store the agent's reply."""
    st.session_state.messages.append({"role": "user", "content": message})
    category, agent_name, reply = run_pipeline(message)
    st.session_state.counts[category] += 1
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "category": category,
        "agent_name": agent_name,
    })


# ---------------------------------------------------------------------------
# Sidebar — mode, live analytics, controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🛍️ ShopEasy")
    st.caption("Multi-Agent Customer Support")

    if llm.is_live():
        st.success("**LIVE** — using the AI API", icon="🟢")
    else:
        st.warning("**MOCK** — offline canned answers", icon="🟡")
        st.caption("Add an API key in `.env` to switch to live AI.")

    st.divider()

    st.subheader("📊 Routing so far")
    counts = st.session_state.counts
    total = sum(counts.values())
    c1, c2, c3 = st.columns(3)
    c1.metric(f"{ICONS['billing']} Billing", counts["billing"])
    c2.metric(f"{ICONS['technical']} Technical", counts["technical"])
    c3.metric(f"{ICONS['general']} General", counts["general"])

    if total:
        st.bar_chart(counts, height=180)
        st.caption(f"{total} message{'s' if total != 1 else ''} handled.")
    else:
        st.caption("No messages yet — ask something to see the routing.")

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.counts = {"billing": 0, "technical": 0, "general": 0}
        st.rerun()


# ---------------------------------------------------------------------------
# Main pane — header, how-it-works, chat
# ---------------------------------------------------------------------------
st.title("🛍️ ShopEasy Multi-Agent Support")
st.caption(
    "Every message flows through two agents: a **🧭 Router** picks the "
    "category, then the matching **Specialist** answers — grounded in the "
    "store's knowledge base."
)

with st.expander("🧠 How the multi-agent flow works"):
    st.markdown(
        """
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
```
The **Router** classifies the message, then hands off to one **Specialist**.
Each agent is just one model call with a different system prompt.
"""
    )

# One-click example prompts (only worth showing before the chat starts).
if not st.session_state.messages:
    st.markdown("**Try one of these:**")
    cols = st.columns(len(EXAMPLES))
    for col, example in zip(cols, EXAMPLES):
        if col.button(example, use_container_width=True):
            handle_user_message(example)
            st.rerun()

# Replay the whole conversation on each run.
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(msg["content"])
    else:
        category = msg["category"]
        with st.chat_message("assistant", avatar=ICONS[category]):
            st.markdown(msg["content"])

# The chat box, pinned to the bottom of the page.
prompt = st.chat_input("Ask about billing, a technical issue, or an order…")
if prompt:
    handle_user_message(prompt)
    st.rerun()
