from smolagents import CodeAgent, OpenAIServerModel

from ai.tools import SQLQueryTool
from resources.constants import OLLAMA_OPENAI_ENDPOINT, DB_FILE
from utils.db_utils import get_table_schema


def expense_agent(model_name: str):
    if model_name == "gemini 2.0 flash lite":
        model = OpenAIServerModel(
            model_id="gemini-2.0-flash-lite",
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key="AIzaSyCTSb4oposEPalcl1wO13EF05yfHs_q9iI",
            temperature=0.7,
        )
    else:
        model = OpenAIServerModel(
            model_id=model_name,
            api_base=OLLAMA_OPENAI_ENDPOINT,
            api_key="ollama",
            temperature=0.7,
        )

    sql_engine = SQLQueryTool()
    sql_engine.description = sql_engine.description + get_table_schema(
        DB_FILE, "expenses"
    )
    agent = CodeAgent(
        tools=[sql_engine],
        model=model,
    )

    return agent
