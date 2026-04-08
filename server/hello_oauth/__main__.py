import os
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from agent_executor import HelloAgentExecutor
from auth import auth_token_var

hello_skill = AgentSkill(
    id="hello",
    name="Hello",
    description="Returns a piratey greeting. No authentication required.",
    tags=["hello", "greeting"],
    examples=["hi", "hello", "hi, i'm bob"],
)

dice_skill = AgentSkill(
    id="roll_dice",
    name="Roll Dice",
    description="Rolls one or more 6-sided dice and returns the results. Requires a valid OAuth token.",
    tags=["dice", "random", "game"],
    examples=["roll 3", "roll 5 dice"],
)

_base_url = os.environ.get("AGENT_BASE_URL")

public_agent_card = AgentCard(
    name="Hello A2A (OAuth)",
    description="Simple agent with a public hello skill and an OAuth-authenticated dice-rolling skill.",
    url=_base_url,
    iconUrl="https://cdn.jsdelivr.net/gh/googlefonts/noto-emoji@main/png/128/emoji_u1f44b.png",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[hello_skill],
    supports_authenticated_extended_card=True,
)

extended_agent_card = public_agent_card.model_copy(
    update={
        "name": "Hello A2A (OAuth)",
        "description": "Full-featured agent including the dice-rolling skill.",
        "version": "1.0.0",
        "skills": [hello_skill, dice_skill],
    }
)

class AuthHeaderMiddleware:
    """Captures the raw Authorization header before the A2A SDK processes the request."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode("latin1")
            auth_token_var.set(auth_header)
        await self.app(scope, receive, send)

request_handler = DefaultRequestHandler(
    agent_executor=HelloAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

server = A2AStarletteApplication(
    agent_card=public_agent_card,
    http_handler=request_handler,
    extended_agent_card=extended_agent_card,
)

app = AuthHeaderMiddleware(server.build())

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)
