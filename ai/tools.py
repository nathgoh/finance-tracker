import pandas as pd

from smolagents import Tool, tool
from datetime import datetime

from utils.json_utils import read_json


class DataFrameQueryTool(Tool):
    name = "dataframe_query"
    description = """
        Allows you to query financial data using pandas operations.
        The tool provides two DataFrames: 'expenses_df' and 'incomes_df'.
        Write a Python expression that uses these DataFrames and returns a result.

        Args:
            query: A valid Python/pandas expression using expenses_df and/or incomes_df.
                   Example: "expenses_df[expenses_df['category'] == 'Grocery']['amount'].sum()"
                   Example: "expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False)"

        Data Schema: \n
    """

    inputs = {
        "query": {
            "type": "string",
            "description": "A valid Python/pandas expression using expenses_df and/or incomes_df",
        }
    }
    output_type = "string"

    def forward(self, query: str) -> str:
        expenses_data = read_json("expenses.json")
        incomes_data = read_json("incomes.json")

        expenses_df = pd.DataFrame(expenses_data["records"])
        incomes_df = pd.DataFrame(incomes_data["records"])

        try:
            result = eval(query, {"__builtins__": {}}, {
                "expenses_df": expenses_df,
                "incomes_df": incomes_df,
                "pd": pd,
            })
            output = str(result)
        except Exception as e:
            raise ValueError(f"Query error: {e}")

        if not output or output.strip() == "":
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
