import streamlit as st

from utils.json_utils import read_json


def init_expense_session_state():
    """
    Initializes the session state variables if they don't exist for the expense input page.
    """

    if "expenses" not in st.session_state:
        st.session_state.expenses = []
    if "categories" not in st.session_state:
        st.session_state.categories = read_json("categories.json")


def init_income_session_state():
    """
    Initializes the session state variables if they don't exist for the income input page.
    """

    if "incomes" not in st.session_state:
        st.session_state.incomes = []
