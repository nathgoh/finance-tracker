import streamlit as st
import plotly.express as px

from utils.expense_utils import get_expenses_df
from utils.income_utils import get_incomes_df

expense_df = get_expenses_df()
income_df = get_incomes_df()

st.title("Finance Dashboard")

expense_pie = px.pie(
    data_frame=expense_df,
    names="category",
    values="amount",
    hole=0.45,
)
expense_pie.update_traces(textinfo="value+percent")

st.write(expense_pie)
