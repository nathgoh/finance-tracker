import streamlit as st

expense_dashboard = st.Page(
    "expenses/expense_dashboard.py",
    title="Expense Dashboard",
    icon=":material/dashboard:",
)
expense_input = st.Page(
    "expenses/expense_input.py", title="Expense Input", icon=":material/payments:"
)

pages = st.navigation({"Expenses": [expense_dashboard, expense_input]})
pages.run()
