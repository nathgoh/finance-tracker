import streamlit as st


def expense_form():
    expense_form = st.form("expense_form")
    expense_form.write("Expense Input")
    expense = expense_form.number_input("Expense")
    categories = expense_form.selectbox(
        "Categories",
        [
            "Personal",
            "Home",
            "Health",
            "Grocery",
            "Entertainment",
            "Transportation",
            "Travel",
            "Misc",
        ],
    )
    note = expense_form.text_input("Notes")
    submit = expense_form.form_submit_button("Submit")
    
    return expense_form
