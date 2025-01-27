import streamlit as st

expense_dashboard = st.Page(
    "expenses/expense_dashboard.py",
    title="Expense Dashboard",
    icon=":material/dashboard:",
)
expense_input = st.Page(
    "expenses/expense_input.py", title="Expense Input", icon=":material/payments:"
)
income_input = st.Page(
    "expenses/income_input.py", title="Income Input", icon=":material/savings:"
)

pages = st.navigation({"Expenses": [expense_dashboard, expense_input, income_input]})
pages.run()
