import os
import sqlite3
import streamlit as st


def get_database_path(file_name) -> str:
    db_dir = os.path.join("./db")

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL
        )
    """)

    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            frequency TEXT,
            recurring_id TEXT,
            FOREIGN KEY (category) REFERENCES categories (category)
        )
    """)

    # Create income table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            source TEXT
        )
    """)

    conn.commit()
    conn.close()
