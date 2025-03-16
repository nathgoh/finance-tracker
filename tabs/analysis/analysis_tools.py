from smolagents import tool

from utils.db_utils import get_db_connection

@tool
def expense_table_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the table. Returns a string representation of the result.
    The table name is "expenses". Its description is as follows:
        Columns:
           - id INTEGER
           - amount FLOAT
           - category TEXT
           - date TEXT (in the format YYYY-MM-DD)
           - notes TEXT
           - frequency TEXT
           - recurring_id TEXT

    Args:
        query: The query to perform. This should be correct SQL.
    """
    
    output = ""
    conn = get_db_connection("finance_tracker.db")
    rows = conn.execute(query)
    for row in rows:
        output += "\n" + str(row)
    
    return output