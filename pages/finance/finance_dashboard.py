import streamlit as st
import plotly.express as px
import pandas as pd

from utils.expense_utils import get_expenses_df
from utils.income_utils import get_incomes_df
from resources.constants import MONTHS_MAP

income_df = get_incomes_df()

st.title("Finance Dashboard")


def expense_charts():
    """
    Expense figures and graphs to visually give a breakdown of your finances.
    """

    # Expense dataframe, reformat to have better looking labels
    expense_df = get_expenses_df()
    reformatted_expense_df = pd.DataFrame(
        {
            "Category": expense_df.category.tolist(),
            "Amount ($)": expense_df.amount.tolist(),
            "Date": pd.to_datetime([date for date in expense_df.date.tolist()]),
        }
    ).set_index("Date")

    # Donut figure showing percentage expense of each category
    expense_pie = px.pie(
        data_frame=reformatted_expense_df,
        names="Category",
        values="Amount ($)",
        hole=0.45,
    )
    expense_pie.update_traces(textinfo="percent")

    # Line chart showing expense per category over each month
    monthly_expense_df = (
        reformatted_expense_df.groupby("Category")
        .resample("ME")
        .sum("Amount ($)")
        .reset_index()
        .set_index("Date")
    )
    monthly_expense_df.index = monthly_expense_df.index.month_name()
    line_chart = px.line(
        monthly_expense_df, x=None, y="Amount ($)", color="Category", symbol="Category"
    )

    return expense_pie, line_chart, monthly_expense_df


def dashboard():
    # Get expense figures/charts
    expense_pie, line_chart, monthly_expense_df = expense_charts()

    col_1, col_2 = st.columns([0.4, 0.6])
    with col_1:
        st.plotly_chart(expense_pie)
    with col_2:
        st.plotly_chart(line_chart)

    avg_month_expense_df = (
        monthly_expense_df.groupby("Date")["Amount ($)"].mean().reset_index()
    )
    avg_month_expense_df.reindex(MONTHS_MAP.keys())
    st.table(avg_month_expense_df)


dashboard()
