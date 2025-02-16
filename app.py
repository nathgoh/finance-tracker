import streamlit as st

from utils.db_utils import init_database

init_database()

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💵",
)

finance_dashboard = st.Page(
    "finance/dashboard.py",
    title="Finance Dashboard",
    icon=":material/dashboard:",
)
expense_input = st.Page(
    "finance/expense_input.py", title="Expense Input", icon=":material/payments:"
)
income_input = st.Page(
    "finance/income_input.py", title="Income Input", icon=":material/savings:"
)
analysis = st.Page("analysis/analysis.py", title="Analysis", icon=":material/insights:")

pages = st.navigation(
    {
        "Finances": [finance_dashboard, expense_input, income_input],
        "Analysis": [analysis],
    }
)
pages.run()
