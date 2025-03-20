import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db_utils import get_db_connection
from utils.expense_utils import get_expenses_df
from utils.income_utils import get_incomes_df
from resources.constants import DB_FILE, MONTHS_MAP

income_df = get_incomes_df()

st.title("Finance Dashboard")


def expense_charts(year) -> tuple:
    """
    Expense figures and graphs to visually give a breakdown of your finances.
    """

    # Expense dataframe, reformat to have better looking labels
    expense_df = get_expenses_df(year)
    expense_pie, line_chart, monthly_expense_df = None, None, pd.DataFrame()
    if not expense_df.empty:
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
            monthly_expense_df,
            x=None,
            y="Amount ($)",
            color="Category",
            symbol="Category",
        )

    return expense_pie, line_chart, monthly_expense_df


def dashboard():
    conn = get_db_connection(DB_FILE)
    sql_str = f"""
        SELECT date
        FROM expenses
    """
    dates = pd.read_sql_query(sql_str, conn)
    conn.close()
    
    years = sorted(pd.to_datetime(dates["date"]).dt.year.unique(), reverse=True)
    year_select = st.selectbox("Select Year", years, index=0)
    if year_select:
        # Get expense figures/charts
        expense_pie, line_chart, monthly_expense_df = expense_charts(year_select)
        if (
            expense_pie is not None
            and line_chart is not None
            and not monthly_expense_df.empty
        ):
            col_1, col_2 = st.columns([0.4, 0.6])
            with col_1:
                st.plotly_chart(expense_pie)
            with col_2:
                st.plotly_chart(line_chart)

            sum_month_expense_df = (
                monthly_expense_df.groupby("Date")["Amount ($)"]
                .sum()
                .reset_index()
                .sort_values(by="Date", key=lambda x: [MONTHS_MAP[m] for m in x])
            ).reset_index(drop=True)
            st.dataframe(
                sum_month_expense_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Amount ($)": st.column_config.NumberColumn(
                        "Amount ($)", format="$%.2f"
                    )
                },
            )


dashboard()
