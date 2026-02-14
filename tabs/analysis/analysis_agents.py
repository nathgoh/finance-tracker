import os

from dotenv import load_dotenv
from smolagents import CodeAgent, OpenAIServerModel

from ai.tools import DataFrameQueryTool, current_year
from resources.constants import LLM_MODELS

from utils.json_utils import get_data_schema

load_dotenv()

OLLAMA_OPENAI_ENDPOINT = os.getenv("OLLAMA_OPENAI_ENDPOINT")


def expense_agent(model_name: str):
    model = OpenAIServerModel(
        model_id=LLM_MODELS.get(model_name),
        api_base=OLLAMA_OPENAI_ENDPOINT,
        api_key="ollama",
        temperature=0.7,
    )

    df_query_tool = DataFrameQueryTool()
    df_query_tool.description = (
        df_query_tool.description
        + get_data_schema("expenses")
        + "\n"
        + get_data_schema("incomes")
    )
    agent = CodeAgent(tools=[df_query_tool, current_year], model=model, max_steps=10)

    return agent
