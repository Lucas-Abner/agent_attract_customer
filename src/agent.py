from agno.agent import Agent
from agno.models.ollama import Ollama



agent = Agent(
    model=Ollama("qwen2.5:7b"),
    markdown=True
)

agent.print_response("Ola")