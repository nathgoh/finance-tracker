import os
import sqlite3
import streamlit as st


def get_database_path(file_name) -> str:
    db_dir = os.path.join("./app/db")

    # Create directory if it doesn't exist
    try:
        os.makedirs(db_dir, exist_ok=True)
    except Exception as e:
        st.error(f"Failed to create directory: {e}")

    return os.path.join(db_dir, file_name)


def get_db_connection(file_name) -> sqlite3.Connection:
    """
    Create a database connection with error handling
    """

    try:
        db_path = get_database_path(file_name)
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        raise e


def init_database():
    """
    Initialize SQLite database and create tables

    Note dates as stored as strings: ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")
    """

    conn = get_db_connection("finance_tracker.db")
    cursor = conn.cursor()

    # Create categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_name TEXT PRIMARY KEY
        )
    """)

    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category INTEGER NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (category) REFERENCES categories (category_name)
        )
    """)

    # Create income table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            source TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_expense_data():
    """
    Save expenses data to SQLite database
    """

    conn = get_db_connection("finance_tracker.db")
    try:
        cursor = conn.cursor()

        # Update categories table
        cursor.execute("DELETE FROM categories")
        cursor.executemany(
            "INSERT INTO categories (category_name) VALUES (?)",
            [(category,) for category in st.session_state.categories],
        )

        # Update expenses table
        for expense in st.session_state.expenses:
            cursor.executemany(
                "INSERT INTO expenses (amount, category, date, notes) VALUES (?, ?, ?, ?)",
                [
                    (
                        expense["Amount"],
                        expense["Category"],
                        expense["Date"],
                        expense["Notes"],
                    )
                ],
            )

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving expense input data: {e}")
    finally:
        conn.close()


def save_income_data():
    """
    Save income data to SQLite database
    """

    conn = get_db_connection("finance_tracker.db")
    try:
        cursor = conn.cursor()

        # Update income table
        for income in st.session_state.incomes:
            cursor.executemany(
                "INSERT INTO income (amount, date, source) VALUES (?, ?, ?)",
                [(income["Amount"], income["Date"], income["Source"])],
            )

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Failed to saving income input data: {e}")
    finally:
        conn.close()
