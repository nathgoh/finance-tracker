import streamlit as st

from finance.expense_input import get_expenses_df

expense_df = get_expenses_df()

st.title("Finance Dashboard")
st.dataframe(expense_df, use_container_width=True)
