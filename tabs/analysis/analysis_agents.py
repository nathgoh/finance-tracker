import os

from dotenv import load_dotenv
from smolagents import CodeAgent, OpenAIServerModel

from ai.tools import SQLQueryTool, current_year
from resources.constants import DB_FILE, LLM_MODELS

from utils.db_utils import get_table_schema

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_OPENAI_ENDPOINT = os.getenv("OLLAMA_OPENAI_ENDPOINT")


def expense_agent(model_name: str):
    if model_name == "Gemini 2.0 Flash Lite":
        model = OpenAIServerModel(
            model_id="gemini-2.0-flash-lite",
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=GEMINI_API_KEY,
            temperature=0.7,
        )
    else:
        model = OpenAIServerModel(
            model_id=LLM_MODELS.get(model_name),
            api_base=OLLAMA_OPENAI_ENDPOINT,
            api_key="ollama",
            temperature=0.7,
        )

    sql_engine = SQLQueryTool()
    sql_engine.description = sql_engine.description + get_table_schema(
        DB_FILE, "expenses"
    )
    agent = CodeAgent(tools=[sql_engine, current_year], model=model, max_steps=10)

    return agent
