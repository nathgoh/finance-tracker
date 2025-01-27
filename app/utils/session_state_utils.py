import sqlite3
import streamlit as st

from db_utils import get_database_path

def init_expense_session_state():
    """
    Initializes the session state variables if they don't exist.
    """
    
    if "expenses" not in st.session_state:
        st.session_state.expenses = []
    if "categories" not in st.session_state:
        # Load categories from SQLite database
        conn = sqlite3.connect(get_database_path("expense_tracker.db"))
        cursor = conn.cursor()
        
        # Get categories from database
        cursor.execute("SELECT category_name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        
        if not categories:
            # Default categories
            default_categories = [
                "Personal",
                "Home",
                "Health",
                "Grocery",
                "Food & Dining"
                "Entertainment",
                "Transportation",
                "Travel",
                "Miscellaneous",
            ]
        
            for category in default_categories:
                cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (category,))
            st.session_state.categories = default_categories
        else:
            st.session_state.categories = categories
        
        conn.commit()
        conn.close()

        
