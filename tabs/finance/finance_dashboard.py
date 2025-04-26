import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db_utils import get_db_connection
from utils.expense_utils import get_expenses_df
from utils.income_utils import get_incomes_df
from resources.constants import DB_FILE, MONTHS_MAP, CATEGORY_COLORS


st.title("Finance Dashboard")


def finance_figures(income_df: pd.DataFrame, expense_df: pd.DataFrame) -> tuple:
    """
    Finance figures and graphs to visually give a breakdown of your expenses and incomes.

    Args:
        income_df (pd.DataFrame): Income dataframe for a given year
        expense_df (pd.DataFrame): Expense dataframe for a given year

    Returns:
        tuple: figures and dataframes giving us the financial breakdown
    """

    expense_bar, finance_chart, monthly_expense_df, sum_month_expense_df = (
        None,
        None,
        pd.DataFrame(),
        pd.DataFrame(),
    )

    reformatted_expense_df = pd.DataFrame(
        {
            "Category": expense_df.category.tolist(),
            "Amount ($)": expense_df.amount.tolist(),
            "Date": pd.to_datetime([date for date in expense_df.date.tolist()]),
        }
    ).set_index("Date")

    # Group by category and sum the amounts
    grouped_expense_df = (
        reformatted_expense_df.groupby("Category")["Amount ($)"]
        .sum()
        .reset_index()
        .round(2)
    )
    total_expense = grouped_expense_df["Amount ($)"].sum()
    grouped_expense_df["Percentage"] = (
        grouped_expense_df["Amount ($)"] / total_expense
    ) * 100
    grouped_expense_df[""] = ""

    # Stacked bar chart of total expense per category
    expense_bar = px.bar(
        data_frame=grouped_expense_df,
        x="Amount ($)",
        y="",
        color="Category",
        orientation="h",
        text="Amount ($)",
        title="Expense Breakdown by Category",
        custom_data=["Category", "Amount ($)", "Percentage"],
        color_discrete_map=CATEGORY_COLORS,
    )
    expense_bar.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.7,
            xanchor="center",
            x=0.5,
        ),
        barmode="stack",
        height=300,
    )
    expense_bar.update_traces(
        texttemplate="<b>$%{customdata[1]}<br><b>%{customdata[2]:.2f}%",
        hovertemplate="<b>%{customdata[0]}</b><br>Amount: $%{customdata[1]}<br>Percentage: %{customdata[2]:.2f}%<extra></extra>",
    )

    # Function to calculate the monthly breakdown for total expense or incomes
    def monthly_total_breakdown(monthly_df, finance_chart, color, name):
        sum_month_df = (
            monthly_df.groupby("Date")["Amount ($)"]
            .sum()
            .reset_index()
            .sort_values(by="Date", key=lambda x: [MONTHS_MAP[m] for m in x])
        ).reset_index(drop=True)
        sum_month_df["Date"] = pd.Categorical(
            sum_month_df["Date"], categories=list(MONTHS_MAP.keys()), ordered=True
        )
        sum_month_df = sum_month_df.sort_values(by="Date")

        # Bar chart showing total expense/income per month
        finance_chart.add_bar(
            x=sum_month_df["Date"],
            y=sum_month_df["Amount ($)"],
            name=name,
            marker=dict(color=color),
            hovertemplate="<b>Date:</b> %{x}<br><b>Amount:</b> $%{y:.2f}<extra></extra>",
        )
        return finance_chart, sum_month_df

    monthly_expense_df = (
        reformatted_expense_df.groupby("Category")
        .resample("ME")
        .sum("Amount ($)")
        .reset_index()
        .set_index("Date")
    )
    monthly_expense_df.index = monthly_expense_df.index.month_name()

    # Line chart showing expense per category over each month
    finance_chart = px.line(
        monthly_expense_df,
        x=None,
        y="Amount ($)",
        color="Category",
        symbol="Category",
        color_discrete_map=CATEGORY_COLORS,
    )

    # Bar chart showing total expense per month
    finance_chart, sum_month_expense_df = monthly_total_breakdown(
        monthly_expense_df, finance_chart, "grey", "Expense"
    )

    reformatted_income_df = pd.DataFrame(
        {
            "Source": income_df.source.tolist(),
            "Amount ($)": income_df.amount.tolist(),
            "Date": pd.to_datetime([date for date in income_df.date.tolist()]),
        }
    ).set_index("Date")
    monthly_income_df = (
        reformatted_income_df.groupby("Source")
        .resample("ME")
        .sum("Amount ($)")
        .reset_index()
        .set_index("Date")
    )
    monthly_income_df.index = monthly_income_df.index.month_name()
    finance_chart, sum_month_income_df = monthly_total_breakdown(
        monthly_income_df, finance_chart, "lightslategrey", "Income"
    )

    sum_month_expense_df = sum_month_expense_df.rename(
        columns={"Amount ($)": "Expense Amount ($)"}
    )
    sum_month_income_df = sum_month_income_df.rename(
        columns={"Amount ($)": "Income Amount ($)"}
    )

    sum_month_finance_df = pd.merge(
        sum_month_expense_df, sum_month_income_df, on="Date", how="outer"
    )

    return expense_bar, finance_chart, monthly_expense_df, sum_month_finance_df


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
        # Expense and income dataframes
        expense_df = get_expenses_df(year_select)
        income_df = get_incomes_df(year_select)

        total_expense = expense_df.amount.sum()
        total_income = income_df.amount.sum()

        # Breakdown of total expense, income and savings
        expense, income, savings = st.columns(3)
        expense.metric(label="Total Expense", value=f"{total_expense.round(2)}$", border=True)
        income.metric(label="Total Income", value=f"{total_income.round(2)}$", border=True)
        savings.metric(
            label="Total Savings", value=f"{(total_income - total_expense).round(2)}$", border=True
        )
        
        # Breakdown of average expense with/without rent, and percentage saved
        avg_expense, avg_expense_no_rent, saved = st.columns(3)
        avg_expense.metric(
            label="Average Expense",
            value=f"{(total_expense / len(expense_df)).round(2)}$",
            border=True,
            )
        avg_expense_no_rent.metric(
            label="Average Expense (No Rent)",
            value=f"{(total_expense / len(expense_df[expense_df['category'].str.lower() != 'rent'])).round(2)}$",
            border=True,
        )
        saved.metric(
            label="% Saved",
            value=f"{((total_income - total_expense) / total_income * 100).round(2)}%",
            border=True,
        )

        # Get finance figures/charts
        expense_bar, finance_chart, monthly_expense_df, sum_month_expense_df = (
            finance_figures(income_df, expense_df)
        )
        if (
            expense_bar is not None
            and finance_chart is not None
            and not monthly_expense_df.empty
        ):
            finance_chart.update_layout(
                xaxis=dict(categoryorder="array", categoryarray=list(MONTHS_MAP.keys()))
            )
            st.plotly_chart(expense_bar)
            st.plotly_chart(finance_chart)
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
