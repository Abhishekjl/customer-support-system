"""
ShopEasy — Multi-Agent Customer Support System
Run:  python main.py

This is the entry point: a simple terminal chat loop.
For every message you type, you can SEE the multi-agent flow:
    Router decides the category  ->  the matching Specialist answers.
"""

import llm
from agents import ROUTER, SPECIALISTS

# A few emoji icons per agent, purely to make the demo readable.
ICONS = {
    "Router": "🧭",
    "billing": "💳",
    "technical": "🛠️",
    "general": "📦",
}


def banner():
    mode = "LIVE (OpenAI API)" if llm.is_live() else "MOCK (offline, no API key)"
    print("=" * 62)
    print("   🛍️  ShopEasy — Multi-Agent Customer Support")
    print(f"   Mode: {mode}")
    print("=" * 62)
    print("Ask anything about billing, a technical issue, or an order.")
    print("Type 'quit' or 'exit' to leave.\n")
    print("Try:  'I want a refund'   |   'I forgot my password'   |   "
          "'Where is my order?'\n")


def handle_message(message):
    """Run one message through the full multi-agent pipeline and print the reply."""
    # Step 1: the Router picks a category.
    category = ROUTER.route(message)

    # Step 2: the matching Specialist answers.
    agent = SPECIALISTS[category]
    reply = agent.handle(message)
    print(f"{ICONS[category]} {agent.name}: {reply}\n")


def main():
    banner()
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! 👋")
            break

        if not message:
            continue
        if message.lower() in {"quit", "exit", "bye"}:
            print("Goodbye! 👋")
            break

        handle_message(message)


if __name__ == "__main__":
    main()
