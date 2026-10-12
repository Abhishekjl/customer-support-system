"""
The agents. This is the heart of the "multi-agent" system.

There are two kinds of agent:
    1. RouterAgent     -> reads the message and decides WHICH specialist handles it
    2. SpecialistAgent -> actually answers, using its own persona + knowledge base

The flow (see main.py) is:
    customer message -> RouterAgent -> one SpecialistAgent -> reply
"""

import llm
from knowledge_base import kb_as_text, best_mock_answer, keyword_in


# ---------------------------------------------------------------------------
# 1) ROUTER AGENT  (a.k.a. triage) — classifies the message into a category
# ---------------------------------------------------------------------------
class RouterAgent:
    name = "Router"
    categories = ["billing", "technical", "general"]

    system_prompt = (
        "You are a triage router for an e-commerce support team.\n"
        "Classify the customer's message into EXACTLY ONE of these categories:\n"
        "- billing: payments, refunds, invoices, charges, pricing, subscriptions\n"
        "- technical: login problems, passwords, bugs, errors, app/website issues\n"
        "- general: orders, shipping, delivery, returns, products, store info, "
        "anything else\n"
        "Reply with ONLY the single category word: billing, technical, or general."
    )

    def route(self, message):
        """Return one category string: 'billing', 'technical', or 'general'."""
        reply = llm.chat(self.system_prompt, message, temperature=0)
        if reply:
            reply = reply.lower()
            for category in self.categories:
                if category in reply:
                    return category
        # Offline / unclear reply -> keyword-based routing.
        return self._mock_route(message)

    def _mock_route(self, message):
        text = message.lower()
        billing_kw = ["refund", "charge", "charged", "payment", "invoice", "bill",
                      "price", "subscription", "money", "paid", "card", "receipt"]
        tech_kw = ["login", "log in", "sign in", "password", "reset", "error",
                   "bug", "crash", "not working", "broken", "access", "app",
                   "website down", "glitch", "locked"]
        if any(keyword_in(text, k) for k in billing_kw):
            return "billing"
        if any(keyword_in(text, k) for k in tech_kw):
            return "technical"
        return "general"


# ---------------------------------------------------------------------------
# 2) SPECIALIST AGENT — one instance per category, each with its own persona
# ---------------------------------------------------------------------------
class SpecialistAgent:
    def __init__(self, name, category, persona):
        self.name = name
        self.category = category
        self.persona = persona

    def _system_prompt(self):
        # The specialist is grounded in its category's FAQ so answers stay on-policy.
        return (
            f"{self.persona}\n\n"
            f"Use the following store policies to answer accurately. "
            f"If the answer isn't covered, be helpful and honest, and offer to "
            f"escalate to a human agent.\n"
            f"--- STORE POLICIES ({self.category}) ---\n"
            f"{kb_as_text(self.category)}\n"
            f"--- END POLICIES ---\n"
            f"Keep replies friendly, short, and clear."
        )

    def handle(self, message):
        """Produce the answer for the customer (live AI or offline fallback)."""
        reply = llm.chat(self._system_prompt(), message)
        if reply:
            return reply
        return self._mock_reply(message)

    def _mock_reply(self, message):
        answer = best_mock_answer(self.category, message)
        if answer:
            return answer
        # Nothing matched — a safe, polite default that still feels on-brand.
        return (
            f"Thanks for reaching out! I'm the {self.name}. I couldn't find an "
            f"exact answer to that, so I'd be happy to connect you with a human "
            f"agent on our team (available 9am-9pm). Could you share a bit more detail?"
        )


# ---------------------------------------------------------------------------
# Build the team once, so main.py can just import and use it.
# ---------------------------------------------------------------------------
ROUTER = RouterAgent()

SPECIALISTS = {
    "billing": SpecialistAgent(
        "Billing Agent", "billing",
        "You are a calm, precise billing support specialist for ShopEasy.",
    ),
    "technical": SpecialistAgent(
        "Technical Agent", "technical",
        "You are a patient technical support specialist for ShopEasy who gives "
        "clear step-by-step fixes.",
    ),
    "general": SpecialistAgent(
        "General Agent", "general",
        "You are a warm, helpful general support specialist for ShopEasy.",
    ),
}
