import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db_utils import get_db_connection
from utils.expense_utils import get_expenses_df
from utils.income_utils import get_incomes_df
from resources.constants import DB_FILE, MONTHS_MAP

income_df = get_incomes_df()

st.title("Finance Dashboard")

@st.cache_data(ttl=3600)
def expense_figures(year: str) -> tuple:
    """
    Expense figures and graphs to visually give a breakdown of your expenses.

    Args:
        year (str): year of finances to breakdown
    Returns:
        tuple: figures and dataframes giving us the expense financial breakdown
    """

    # Expense dataframe, reformat to have better looking labels
    expense_df = get_expenses_df(year)
    expense_bar, expense_chart, monthly_expense_df, sum_month_expense_df = (
        None,
        None,
        pd.DataFrame(),
        pd.DataFrame(),
    )
    if not expense_df.empty:
        reformatted_expense_df = pd.DataFrame(
            {
                "Category": expense_df.category.tolist(),
                "Amount ($)": expense_df.amount.tolist(),
                "Date": pd.to_datetime([date for date in expense_df.date.tolist()]),
            }
        ).set_index("Date")

        # Group by category and sum the amounts
        grouped_expense_df = (
            reformatted_expense_df.groupby("Category")["Amount ($)"].sum().reset_index().round(2)
        )
        total_expense = grouped_expense_df["Amount ($)"].sum()
        grouped_expense_df["Percentage"] = (
            grouped_expense_df["Amount ($)"] / total_expense
        ) * 100
        grouped_expense_df[""] = ""

        # Stacked bar chart
        expense_bar = px.bar(
            data_frame=grouped_expense_df,
            x="Amount ($)",
            y="",
            color="Category",
            orientation="h",
            text="Amount ($)",
            title="Expense Breakdown by Category",
            custom_data=["Category", "Amount ($)", "Percentage"],
        )
        expense_bar.update_layout(barmode="stack", height=300)
        expense_bar.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Amount: $%{customdata[1]}<br>Percentage: %{customdata[2]:.2f}%<extra></extra>"
        )

        # Line chart showing expense per category over each month
        monthly_expense_df = (
            reformatted_expense_df.groupby("Category")
            .resample("ME")
            .sum("Amount ($)")
            .reset_index()
            .set_index("Date")
        )
        monthly_expense_df.index = monthly_expense_df.index.month_name()
        sum_month_expense_df = (
            monthly_expense_df.groupby("Date")["Amount ($)"]
            .sum()
            .reset_index()
            .sort_values(by="Date", key=lambda x: [MONTHS_MAP[m] for m in x])
        ).reset_index(drop=True)
        expense_chart = px.line(
            monthly_expense_df,
            x=None,
            y="Amount ($)",
            color="Category",
            symbol="Category",
        )
        expense_chart.add_bar(
            x=sum_month_expense_df["Date"],
            y=sum_month_expense_df["Amount ($)"],
            name="Total",
            showlegend=False,
            marker=dict(color="grey"),
            hovertemplate="<b>Date:</b> %{x}<br><b>Amount:</b> $%{y:.2f}<extra></extra>",
        )

    return expense_bar, expense_chart, monthly_expense_df, sum_month_expense_df


def dashboard():
    conn = get_db_connection(DB_FILE)
    sql_str = """
        SELECT date
        FROM expenses
    """
    dates = pd.read_sql_query(sql_str, conn)
    conn.close()

    years = sorted(pd.to_datetime(dates["date"]).dt.year.unique(), reverse=True)
    year_select = st.selectbox("Select Year", years, index=0)
    if year_select:
        # Get expense figures/charts
        expense_bar, expense_chart, monthly_expense_df, sum_month_expense_df = (
            expense_figures(year_select)
        )
        if (
            expense_bar is not None
            and expense_chart is not None
            and not monthly_expense_df.empty
        ):
            st.plotly_chart(expense_bar)
            st.plotly_chart(expense_chart)
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
