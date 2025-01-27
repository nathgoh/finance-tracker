import os
import sqlite3
import streamlit as st

def get_database_path(file_name):
    return os.path.join("/app/db", file_name)

def init_database():
    """
    Initialize SQLite database and create tables
    
    Note dates as stored as strings: ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")
    """
    
    conn = sqlite3.connect(get_database_path("expense_tracker.db"))
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
            notes TEXT
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
    
    conn = sqlite3.connect(get_database_path("expense_tracker.db"))
    cursor = conn.cursor()
    
    # Update categories table
    cursor.execute("DELETE FROM categories")
    cursor.executemany("INSERT INTO categories (category_name) VALUES (?)", [(category,) for category in st.session_state.categories])
    
    # Update expenses table
    cursor.execute("DELETE FROM expenses")
    cursor.executemany("INSERT INTO expenses (amount, category, date, notes) VALUES (?, ?, ?, ?)", st.session_state.expenses)
    
    conn.commit()