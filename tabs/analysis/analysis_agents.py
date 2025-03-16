from smolagents import CodeAgent, LiteLLMModel

from resources.constants import OLLAMA_ENDPOINT
from .analysis_tools import expense_table_engine


def expense_agent(model_name: str) -> CodeAgent:    
    model = LiteLLMModel(model_id=f"ollama_chat/{model_name}", api_base=OLLAMA_ENDPOINT)
    agent = CodeAgent(
        tools=[expense_table_engine],
        model=model
    )
    
    return agent