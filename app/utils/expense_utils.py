from datetime import datetime

import pandas as pd
import sqlite3
import streamlit as st

from utils.db_utils import get_db_connection
from resources.contants import DB_FILE


def get_expenses_df(date=str(datetime.now().year)) -> pd.DataFrame:
    """
    Gets a DataFrame of expenses from the database and session state.

    Returns a DataFrame containing all expenses from the database.
    """

    conn = get_db_connection("finance_tracker.db")
    
    sql_str = f"""
        SELECT amount, category, date, notes
        FROM expenses
        WHERE date LIKE '{date}%'
    """
    
    return pd.read_sql_query(sql_str, conn)


def save_expense_data():
    """
    Save expenses data to SQLite database
    """

    conn = get_db_connection(DB_FILE)
    try:
        c = conn.cursor()

        # Get the most recent expense (the one just added)
        new_expense = st.session_state.expenses[-1]

        # Get category (or insert it into the categories table if doesn't exist)
        c.execute(
            "SELECT category FROM categories WHERE category = ?",
            (new_expense["Category"],),
        )
        result = c.fetchone()

        if result:
            category = result[0]
        else:
            c.execute(
                "INSERT INTO categories (category) VALUES (?)",
                (new_expense["Category"],),
            )
            category = c.lastrowid

        # Insert the expense
        c.execute(
            """
            INSERT INTO expenses (amount, category, date, notes)
            VALUES (?, ?, ?, ?)
        """,
            (
                new_expense["Amount"],
                category,
                new_expense["Date"],
                new_expense["Notes"],
            ),
        )

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving expense input data: {e}")
    finally:
        conn.close()
