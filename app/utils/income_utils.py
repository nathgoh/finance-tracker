import pandas as pd
import sqlite3
import streamlit as st

from utils.db_utils import get_db_connection
from resources.contants import DB_FILE


def get_incomes_df() -> pd.DataFrame:
    """
    Gets a DataFrame of incomes from the database and session state.

    Returns a DataFrame containing all incomes from the database.
    """

    conn = get_db_connection("finance_tracker.db")
    return pd.read_sql_query("SELECT amount, date, source FROM incomes", conn)


def save_income_data():
    """
    Save income data to SQLite database
    """

    conn = get_db_connection(DB_FILE)
    try:
        c = conn.cursor()

        # Update income table
        for income in st.session_state.incomes:
            c.executemany(
                "INSERT INTO income (amount, date, source) VALUES (?, ?, ?)",
                [(income["Amount"], income["Date"], income["Source"])],
            )

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving income input data: {e}")
    finally:
        conn.close()
