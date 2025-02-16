import pandas as pd
import sqlite3
import streamlit as st

from datetime import datetime

from utils.db_utils import get_db_connection
from resources.constants import DB_FILE


def get_incomes_df(date=str(datetime.now().year)) -> pd.DataFrame:
    """
    Gets a DataFrame of incomes from the database and session state.

    Returns a DataFrame containing all incomes from the database.
    """

    conn = get_db_connection("finance_tracker.db")
    return pd.read_sql_query(
        f"""SELECT id, amount, date, source FROM incomes WHERE date LIKE '{date}%'""",
        conn,
    )


def save_income_data():
    """
    Save income data to SQLite database
    """

    conn = get_db_connection(DB_FILE)
    try:
        c = conn.cursor()

        new_income = st.session_state.incomes[-1]
        c.execute(
            "INSERT INTO incomes (amount, date, source) VALUES (?, ?, ?)",
            (new_income["Amount"], new_income["Date"], new_income["Source"]),
        )

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving income input data: {e}")
    finally:
        conn.close()


def delete_income_data(income_ids: list):
    """
    Delete incomes from the database based on their primary key values.
    """
    conn = get_db_connection(DB_FILE)
    if income_ids:
        try:
            c = conn.cursor()
            c.execute(
                f"""
                DELETE FROM incomes
                WHERE id {f"IN {tuple(income_ids)}" if len(income_ids) > 1 else f"= {income_ids[0]}"}
                """
            )
            conn.commit()
            st.success("Income(s) deleted successfully!")
        except sqlite3.Error as e:
            st.error(f"Failed to delete income data: {e}")
        finally:
            conn.close()
