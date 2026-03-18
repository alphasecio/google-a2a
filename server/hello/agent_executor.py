import os
import random
from typing import List
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

def say_hello() -> str:
    """Greets the user in a piratey slang."""
    return "Ahoy, matey! Welcome aboard, ye scallywag! 🏴‍☠️"

def roll_dice(n_dice: int) -> List[int]:
    """Rolls n_dice 6-sided dice and returns the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

def _get_valid_token() -> str:
    token = os.environ.get("AGENT_API_TOKEN")
    if not token:
        raise RuntimeError("AGENT_API_TOKEN environment variable is not set.")
    return token

class HelloAgentExecutor(AgentExecutor):
    """Handles both the public 'hello' skill and the authenticated 'roll_dice' skill."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Pull the raw user text from the first text part of the message.
        user_text = ""
        if context.message and context.message.parts:
            for part in context.message.parts:
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    user_text = part.root.text.strip().lower()
                    break

        # ── Authenticated skill: roll_dice ──────────────────────────────────
        if user_text.startswith("roll"):
            auth_header = context.metadata.get("authorization") or context.metadata.get("Authorization", "")
            token = auth_header.removeprefix("Bearer ").strip()

            if token != _get_valid_token():
                await event_queue.enqueue_event(
                    new_agent_text_message("❌ Unauthorized: a valid Bearer token is required to roll dice.")
                )
                return

            # Parse optional number of dice, e.g. "roll 3" or just "roll"
            parts = user_text.split()
            try:
                n_dice = int(parts[1]) if len(parts) > 1 else 1
            except (ValueError, IndexError):
                n_dice = 1

            results = roll_dice(n_dice)
            total = sum(results)
            msg = f"🎲 Rolled {n_dice}d6 → {results}  (total: {total})"
            await event_queue.enqueue_event(new_agent_text_message(msg))
            return

        # ── Public skill: hello (default / fallback) ────────────────────────
        await event_queue.enqueue_event(new_agent_text_message(say_hello()))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")
