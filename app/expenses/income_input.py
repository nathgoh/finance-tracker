from datetime import datetime

import streamlit as st
import pandas as pd


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
        submit = st.form_submit_button("Add income")

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


def get_incomes_df():
    """
    Converts the list of incomes in the session state to a Pandas DataFrame.

    Returns:
        DataFrame: A DataFrame containing the incomes, with the 'date' column
        converted to datetime format. If there are no incomes, an empty
        DataFrame is returned.
    """

    if st.session_state.incomes:
        df = pd.DataFrame(st.session_state.incomes)
        df["date"] = pd.to_datetime(df["date"])
        return df
    return pd.DataFrame()

def income_input_page():
    """
    Renders a Streamlit page for adding and managing incomes.

    The page includes:

    1. A form for adding a new income.
    2. A section for managing income categories, with options to edit or delete existing categories.
    """
    income_form()


income_input_page()
