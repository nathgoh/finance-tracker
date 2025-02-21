import streamlit as st

from utils.db_utils import init_database

init_database()

st.set_page_config(
    page_title="Finance App",
    page_icon="💵",
)

# Finance tracking
finance_dashboard = st.Page(
    "pages/finance/finance_dashboard.py",
    title="Finance Dashboard",
    icon=":material/dashboard:",
)
expense_input = st.Page(
    "pages/finance/expense_input.py", title="Expense Input", icon=":material/payments:"
)
income_input = st.Page(
    "pages/finance/income_input.py", title="Income Input", icon=":material/savings:"
)
# Finance analysis
analysis_dashboard = st.Page(
    "pages/analysis/analysis_dashboard.py", title="Analysis", icon=":material/insights:"
)
trading_dashboard = st.Page(
    "pages/trading/trading_dashboard.py", title="Trading", icon=":material/trending_up:"
)


pages = st.navigation(
    {
        "Finances": [
            finance_dashboard,
            analysis_dashboard,
            expense_input,
            income_input,
        ],
        "Trading": [trading_dashboard],
    }
)
pages.run()
