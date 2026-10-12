"""
The "knowledge base" (KB) for our fake e-commerce store, "ShopEasy".

Each support category has a short list of FAQ entries. Each entry has:
    - keywords: words we look for to pick this answer in offline mock mode
    - answer:   the canned reply / reference text

How it is used:
    * LIVE mode  -> the whole category's FAQ text is given to the AI as context
                    so its answers stay accurate to our store's policies.
    * MOCK mode  -> we keyword-match the customer's message to the best entry.
"""

import re


def keyword_in(text, keyword):
    """
    True if `keyword` appears in `text` as a whole word/phrase.
    We use word boundaries so 'app' does NOT match 'wrapping', etc.
    """
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None

KNOWLEDGE_BASE = {
    "billing": [
        {
            "keywords": ["refund", "money back", "return my money"],
            "answer": (
                "Refunds are processed within 5-7 business days to your original "
                "payment method. You can request one from Orders > Select order > "
                "'Request refund', as long as it's within 30 days of delivery."
            ),
        },
        {
            "keywords": ["charge", "charged", "double", "extra"],
            "answer": (
                "If you see an unexpected or duplicate charge, it is usually a "
                "temporary authorization hold that clears in 3-5 business days. "
                "If it does not clear, share the order ID and we'll investigate."
            ),
        },
        {
            "keywords": ["invoice", "receipt", "bill"],
            "answer": (
                "You can download an invoice/receipt for any order from "
                "Orders > Select order > 'Download invoice' (PDF)."
            ),
        },
        {
            "keywords": ["payment method", "card", "upi", "paypal", "pay with"],
            "answer": (
                "We accept credit/debit cards, UPI, PayPal, and store gift cards. "
                "You can manage saved payment methods under Account > Payments."
            ),
        },
        {
            "keywords": ["subscription", "cancel plan", "membership", "renew"],
            "answer": (
                "You can cancel or change your ShopEasy Plus membership anytime from "
                "Account > Membership. Cancelling stops the next renewal; current "
                "benefits stay active until the period ends."
            ),
        },
    ],
    "technical": [
        {
            "keywords": ["password", "reset", "forgot"],
            "answer": (
                "To reset your password, go to the login page and click "
                "'Forgot password'. You'll get a reset link by email within a "
                "few minutes (check spam if you don't see it)."
            ),
        },
        {
            "keywords": ["login", "log in", "sign in", "can't access", "locked"],
            "answer": (
                "If you can't log in, first try resetting your password. If your "
                "account is locked after several failed attempts, it unlocks "
                "automatically after 30 minutes."
            ),
        },
        {
            "keywords": ["error", "bug", "crash", "not working", "broken", "glitch"],
            "answer": (
                "Sorry about the trouble. Please try: (1) refresh the page, "
                "(2) clear your browser cache, (3) update the app to the latest "
                "version. If the error has a code, send it to us and we'll dig in."
            ),
        },
        {
            "keywords": ["website down", "site down", "page not loading", "slow"],
            "answer": (
                "If the site won't load, check status.shopeasy.example for outages. "
                "Otherwise it's usually a local network/cache issue — try a "
                "different browser or device to confirm."
            ),
        },
        {
            "keywords": ["app", "update", "install", "version"],
            "answer": (
                "Make sure you're on the latest app version from your app store. "
                "Many bugs are fixed by updating and restarting the app."
            ),
        },
    ],
    "general": [
        {
            "keywords": ["shipping", "delivery", "how long", "arrive", "track"],
            "answer": (
                "Standard shipping takes 3-5 business days; express takes 1-2. "
                "You can track any order under Orders > 'Track package'."
            ),
        },
        {
            "keywords": ["return", "exchange", "send back"],
            "answer": (
                "Items can be returned or exchanged within 30 days if unused and "
                "in original packaging. Start from Orders > 'Return or exchange'."
            ),
        },
        {
            "keywords": ["order status", "where is my order", "order"],
            "answer": (
                "You can see live order status (confirmed, packed, shipped, "
                "delivered) under Orders. We also email you at each step."
            ),
        },
        {
            "keywords": ["hours", "timing", "open", "support hours", "contact"],
            "answer": (
                "Our support team is available 9am-9pm, 7 days a week. This AI "
                "assistant is available 24/7 for common questions."
            ),
        },
        {
            "keywords": ["product", "stock", "available", "size", "color"],
            "answer": (
                "Product availability, sizes, and colors are shown on each product "
                "page. Out-of-stock items have a 'Notify me' button."
            ),
        },
    ],
}


def kb_as_text(category):
    """Return a category's FAQ as plain text, to feed the AI as context (live mode)."""
    entries = KNOWLEDGE_BASE.get(category, [])
    lines = [f"- {entry['answer']}" for entry in entries]
    return "\n".join(lines)


def best_mock_answer(category, message):
    """
    Offline fallback: find the FAQ entry whose keywords best match the message.
    Returns the matching answer, or None if nothing matches.
    """
    text = message.lower()
    best = None
    best_score = 0
    for entry in KNOWLEDGE_BASE.get(category, []):
        score = sum(1 for kw in entry["keywords"] if keyword_in(text, kw))
        if score > best_score:
            best_score = score
            best = entry["answer"]
    return best
