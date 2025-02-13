from datetime import datetime

import streamlit as st

from utils.income_utils import save_income_data
from utils.session_state_utils import init_income_session_state


def income_form():
    """
    Renders a form for adding a new income. The form contains fields for:
    - income amount
    - category selection
    - date selection
    - notes text input

    When the form is submitted, the add_income function is called with the
    form values as arguments. If the form is submitted successfully,
    a success message is displayed.
    """

    st.subheader("Add a New Income")
    with st.form("income_form"):
        income = st.number_input("Income", min_value=0.0, step=0.01, format="%.2f")
        date = st.date_input("Date", datetime.now())
        source = st.text_input("Source")
        submit = st.form_submit_button("Add Income")

    if submit:
        add_income(income, date, source)
        st.success("Income added successfully!")


def add_income(amount, date, source):
    """
    Adds a new income to the session state.

    Parameters:
        amount (float): The income amount.
        date (datetime): The date of the income.
        source (str): Source of the income.
    """

    income = {
        "Amount": amount,
        "Date": date.strftime("%Y-%m-%d"),
        "Source": source,
    }
    st.session_state.incomes.append(income)
    save_income_data()


def income_input_page():
    """
    Renders a Streamlit page for adding and managing incomes.
    """

    init_income_session_state()
    income_form()


income_input_page()
