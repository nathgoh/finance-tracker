from smolagents import CodeAgent, LiteLLMModel

from resources.constants import OLLAMA_ENDPOINT, DB_FILE
from .analysis_tools import expense_table_engine
from utils.db_utils import inspect_table_in_db


def expense_agent(model_name: str) -> CodeAgent:
    table_description = inspect_table_in_db(DB_FILE, "expenses")
    model = LiteLLMModel(model_id=f"ollama_chat/{model_name}", api_base=OLLAMA_ENDPOINT)
    
    expense_table_engine.description = table_description
    agent = CodeAgent(tools=[expense_table_engine], model=model)
    
    return agent
