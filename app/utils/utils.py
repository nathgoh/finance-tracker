import pandas as pd

from utils.db_utils import get_db_connection


def get_expenses_df() -> pd.DataFrame:
    """
    Gets a DataFrame of expenses from the database and session state.

    Returns a DataFrame containing all expenses from the database.
    """

    conn = get_db_connection("finance_tracker.db")
    return pd.read_sql_query("SELECT amount, category, date, notes FROM expenses", conn)


def get_incomes_df() -> pd.DataFrame:
    """
    Gets a DataFrame of incomes from the database and session state.

    Returns a DataFrame containing all incomes from the database.
    """

    conn = get_db_connection("finance_tracker.db")
    return pd.read_sql_query("SELECT amount, date, source FROM incomes", conn)
