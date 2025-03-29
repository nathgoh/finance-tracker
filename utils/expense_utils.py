import pandas as pd
import sqlite3
import streamlit as st

from utils.db_utils import get_db_connection
from resources.constants import DB_FILE


def get_expenses_df(year: None | str = None) -> pd.DataFrame:
    """
    Gets a DataFrame of expenses from the database and session state.

    Args:
        year (None | str, optional): Filter expenses by year. Defaults to None.

    Returns a DataFrame containing all expenses from the database.
    """

    conn = get_db_connection(DB_FILE)

    sql_str = """
        SELECT id, amount, category, date, notes
        FROM expenses
    """
    sql_str += f"""WHERE date LIKE '{year}%'""" if year else ""
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
            INSERT INTO expenses (amount, category, date, notes, frequency, recurring_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                new_expense["Amount"],
                category,
                new_expense["Date"],
                new_expense["Notes"],
                new_expense["Frequency"],
                new_expense["Recurring ID"],
            ),
        )

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving expense input data: {e}")
    finally:
        conn.close()


def delete_expense_data(expense_ids: list):
    """
    Delete expenses from the database based on their primary key values.

    Args:
        expense_ids (list): List of expense ids to be deleted
    """

    conn = get_db_connection(DB_FILE)
    if expense_ids:
        try:
            c = conn.cursor()
            c.execute(
                f"""
                DELETE FROM expenses
                WHERE id {f"IN {tuple(expense_ids)}" if len(expense_ids) > 1 else f"= {expense_ids[0]}"}
                """
            )
            conn.commit()
            st.success("Expense(s) deleted successfully!")
        except sqlite3.Error as e:
            st.error(f"Failed to delete expense data: {e}")
        finally:
            conn.close()


def manage_categories_data(
    new_category: str | None, delete_category: str | None, update_category: list | None
):
    """
    Manages the categories of expenses.

    Args:
        new_category (str | None): Potential new category to add.
        delete_category (str | None): Potential category to delete.
        update_category (str | None): Potential category to update.
    """

    conn = get_db_connection(DB_FILE)
    try:
        c = conn.cursor()
        if new_category:
            c.execute("INSERT INTO categories (category) VALUES (?)", (new_category,))
        elif delete_category:
            c.execute("DELETE FROM categories WHERE category = ?", (delete_category,))
        elif update_category:
            c.execute(
                "UPDATE categories SET category = ? WHERE category = ?",
                (
                    update_category[1],
                    update_category[0],
                ),
            )
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving category input data: {e}")
    finally:
        conn.close()
