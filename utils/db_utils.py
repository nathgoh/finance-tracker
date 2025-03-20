import os
import sqlite3
import streamlit as st

from sqlalchemy import (
    create_engine,
    inspect,
)


def get_database_path(db_file_name: str) -> str:
    """
    Get database path

    Args:
        db_file_name (str): file name where database lives

    Returns:
        str: path where database is located
    """

    db_dir = os.path.join("./db")

    # Create directory if it doesn't exist
    try:
        os.makedirs(db_dir, exist_ok=True)
    except Exception as e:
        st.error(f"Failed to create directory: {e}")

    return os.path.join(db_dir, db_file_name)


def get_db_connection(db_file_name: str) -> sqlite3.Connection:
    """
    Create a database connection with error handling

    Args:
        db_file_name (str): file name where database lives

    Returns:
        sqlite3.Connection: connection to access the database
    """

    try:
        db_path = get_database_path(db_file_name)
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        raise e


def inspect_table_in_db(db_file_name: str, table_name: str):
    """
    Inspect a table in a database to get column information

    Args:
        db_file_name (str): file name where database lives
        table_name (str): name of table to inspect

    Returns:
        str: table description of the column names and their types
    """

    engine = create_engine(f"sqlite:///{get_database_path(db_file_name)}")
    inspector = inspect(engine)
    columns_info = [
        (col["name"], col["type"]) for col in inspector.get_columns(table_name)
    ]

    table_description = "Columns:\n" + "\n".join(
        [f"  - {name}: {col_type}" for name, col_type in columns_info]
    )
    return table_description


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
