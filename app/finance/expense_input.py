from datetime import datetime

import streamlit as st
import pandas as pd

from utils.db_utils import get_db_connection, save_expense_data
from utils.session_state_utils import init_expense_session_state


def expense_form():
    """
    Renders a form for adding a new expense. The form contains fields for:
    - expense amount
    - category selection
    - date selection
    - notes text input

    When the form is submitted, the add_expense function is called with the
    form values as arguments. If the form is submitted successfully,
    a success message is displayed.
    """

    st.subheader("Add a New Expense")
    with st.form("expense_form", clear_on_submit=True):
        expense = st.number_input("Expense", min_value=0.0, step=0.01, format="%.2f")
        category = st.selectbox("Categories", st.session_state.categories)
        date = st.date_input("Date", datetime.now())
        notes = st.text_input("Notes")
        submit = st.form_submit_button("Add Expense")

    if submit:
        add_expense(expense, category, date, notes)
        st.success("Expense added successfully!")


def add_expense(amount, category, date, notes):
    """
    Adds a new expense to the session state.

    Parameters:
        amount (float): The expense amount.
        category (str): The category for the expense.
        date (datetime): The date of the expense.
        notes (str): Additional notes for the expense.

    The expense is stored as a dictionary with keys 'Amount', 'Category', 'Date', and 'Notes',
    and appended to the 'expenses' list in the session state.
    """

    expense = {
        "Amount": amount,
        "Category": category,
        "Date": date.strftime("%Y-%m-%d"),
        "Notes": notes,
    }
    st.session_state.expenses.append(expense)
    save_expense_data()


def get_expenses_df() -> pd.DataFrame:
    """
    Gets a DataFrame of expenses from the database and session state.

    Returns a DataFrame containing all expenses from the database and session state.
    If there are no expenses in the session state, only the database expenses are returned.
    """

    conn = get_db_connection("finance_tracker.db")
    return pd.read_sql_query("SELECT amount, category, date, notes FROM expenses", conn)


def manage_categories():
    """
    Manages the categories of expenses.

    This function displays a sidebar with the following components:

    1. A text input to add a new category.
    2. A button to add the new category.
    3. A list of existing categories with text inputs to edit their names.
    4. Update buttons to save the changes to each category.
    5. Delete buttons to remove each category.

    The function also handles the logic for updating and deleting categories,
    including updating the names of expenses with the same category and
    removing the category from the session state.
    """

    with st.sidebar.expander("Manage Categories"):
        # Add new category
        new_category = st.text_input("Add New Category")
        if st.button("Add Category"):
            if new_category and new_category not in st.session_state.categories:
                st.session_state.categories.append(new_category)
                save_expense_data()
                st.success(f"Added category: {new_category}")
            elif new_category in st.session_state.categories:
                st.error("Category already exists!")

        st.divider()

        # Edit/Delete categories
        st.subheader("Edit Categories")
        for idx, category in enumerate(st.session_state.categories):
            with st.container():
                # Category name input
                new_name = st.text_input(
                    f"Category {idx+1}", value=category, key=f"cat_{idx}"
                )

                # Update and Delete button in two columns
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(
                        "Update", key=f"update_{idx}", use_container_width=True
                    ):
                        if new_name != category:
                            # Update category name in expenses
                            for expense in st.session_state.expenses:
                                if expense["category"] == category:
                                    expense["category"] = new_name

                            # Update category list
                            st.session_state.categories[idx] = new_name
                            save_expense_data()
                            st.success(f"Updated: {category} → {new_name}")

                with col2:
                    if st.button(
                        "Delete", key=f"delete_{idx}", use_container_width=True
                    ):
                        if len(st.session_state.categories) > 1:
                            df = get_expenses_df()
                            if not df.empty and (df["category"] == category).any():
                                st.error(f"Category '{category}' has expenses!")
                            else:
                                st.session_state.categories.remove(category)
                                save_expense_data()
                                st.success(f"Deleted: {category}")
                                st.rerun()
                        else:
                            st.error("Cannot delete last category!")


def expense_input_page():
    """
    Renders a Streamlit page for adding and managing expenses.
    """

    manage_categories()
    expense_form()


init_expense_session_state()
expense_input_page()
