from smolagents import Tool, tool
from sqlalchemy import create_engine, text
from datetime import datetime

from resources.constants import DB_FILE
from utils.db_utils import get_database_path


class SQLQueryTool(Tool):
    name = "sql_engine"
    description = """
        Allows you to perform SQL queries on tables. Returns a string representation of the result.
        Args:
            query: The query to perform. This should be correct SQL.
            
        Table description: \n
    """

    inputs = {
        "query": {
            "type": "string",
            "description": "Enter a valid SQL query",
        }
    }
    output_type = "string"

    def forward(self, query: str):
        engine = create_engine(f"sqlite:///{get_database_path(DB_FILE)}")

        try:
            output = ""
            with engine.connect() as con:
                rows = con.execute(text(query))
                for row in rows:
                    output += "\n" + str(row)
        except Exception as e:
            raise ValueError(f"Full trace: {e}")

        if output == "":
            output = "No results found. Please try another query."

        return output


@tool
def current_year() -> int:
    """
    Returns the current year.

    Returns:
        int: year
    """

    return datetime.today().year
