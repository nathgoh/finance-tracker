import pandas as pd

from utils.db_utils import get_db_connection


def get_expenses_df() -> pd.DataFrame:
    """
    Gets a DataFrame of expenses from the database and session state.

    Returns a DataFrame containing all expenses from the database and session state.
    If there are no expenses in the session state, only the database expenses are returned.
    """

    conn = get_db_connection("finance_tracker.db")
    return pd.read_sql_query("SELECT amount, category, date, notes FROM expenses", conn)
