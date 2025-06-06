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

    category_expense_bar, finance_chart, monthly_expense_df, sum_month_expense_df = (
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
    grouped_category_expense_df = (
        reformatted_expense_df.groupby("Category")["Amount ($)"]
        .sum()
        .reset_index()
        .round(2)
    )
    total_expense = grouped_category_expense_df["Amount ($)"].sum()
    grouped_category_expense_df["Percentage"] = (
        grouped_category_expense_df["Amount ($)"] / total_expense
    ) * 100
    grouped_category_expense_df[""] = ""

    # Stacked bar chart of total expense per category
    category_expense_bar = px.bar(
        data_frame=grouped_category_expense_df,
        x="Amount ($)",
        y="",
        color="Category",
        orientation="h",
        text="Amount ($)",
        title="Expense Breakdown by Category",
        custom_data=["Category", "Amount ($)", "Percentage"],
        color_discrete_map=CATEGORY_COLORS,
    )
    category_expense_bar.update_layout(
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
    category_expense_bar.update_traces(
        texttemplate="<b>$%{customdata[1]}<br><b>%{customdata[2]:.2f}%",
        hovertemplate="<b>%{customdata[0]}</b><br>Amount: $%{customdata[1]}<br>Percentage: %{customdata[2]:.2f}%<extra></extra>",
    )

    # Function to calculate the monthly breakdown (i.e. total amount for each category) for total expense or incomes
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

    # Add income to finance chart
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

    # Total monthly expense
    sum_month_expense_df = sum_month_expense_df.rename(
        columns={"Amount ($)": "Expense Amount ($)"}
    )
    
    # Total monthly income
    sum_month_income_df = sum_month_income_df.rename(
        columns={"Amount ($)": "Income Amount ($)"}
    )

    # Total monthly expense and income
    sum_month_finance_df = pd.merge(
        sum_month_expense_df, sum_month_income_df, on="Date", how="outer"
    )

    return category_expense_bar, finance_chart, sum_month_finance_df


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

        # Total expenses & incomes
        total_expense = expense_df.amount.sum()
        total_income = income_df.amount.sum()
        total_savings = total_income - total_expense
        total_expense_no_rent = expense_df[expense_df["category"].str.lower() != "rent"].amount.sum()

        # Breakdown of total expense, income and savings
        expense, income, savings = st.columns(3)
        expense.metric(label="Total Expense", value=f"{total_expense.round(2)}$", border=True)
        income.metric(label="Total Income", value=f"{total_income.round(2)}$", border=True)
        savings.metric(
            label="Total Savings", value=f"{total_savings.round(2)}$", border=True
        )
        
        # Get finance figures/charts
        category_expense_bar, finance_chart, sum_month_finance_df = (
            finance_figures(income_df, expense_df)
        )

        if (
            category_expense_bar is not None
            and finance_chart is not None
        ):
            
            # Breakdown of average expense with/without rent per month, and percentage saved
            avg_expense, avg_expense_no_rent, saved = st.columns(3)
            avg_expense.metric(
                label="Avg Expense / Month",
                value=f"{(total_expense / len(sum_month_finance_df)).round(2)}$",
                border=True,
                )
            avg_expense_no_rent.metric(
                label="Avg Expense / Month (No Rent)",
                value=f"{(total_expense_no_rent / len(sum_month_finance_df)).round(2)}$",
                border=True,
            )
            saved.metric(
                label="% Saved",
                value=f"{(total_savings / total_income * 100).round(2)}%",
                border=True,
            )

            finance_chart.update_layout(
                xaxis=dict(categoryorder="array", categoryarray=list(MONTHS_MAP.keys()))
            )
            st.plotly_chart(category_expense_bar)
            st.plotly_chart(finance_chart)
            
            st.subheader("Monthly Averages by Category")
            
            # Calculate total expense per category and divide by the current month
            expense_df["date"] = pd.to_datetime(expense_df["date"])
            current_month = expense_df["date"].dt.month.max()
            monthly_avg_df = (
                expense_df.groupby("category")["amount"]
                .sum()
                .div(current_month)
                .round(2)
                .reset_index()
                .rename(columns={"amount": "Monthly Average ($)"})
                .sort_values("Monthly Average ($)", ascending=False)
            )
            
            selected_category = st.selectbox(
                "Select a category to see monthly average:",
                ["All Categories"] + monthly_avg_df["category"].tolist()
            )
            
            if selected_category != "All Categories":
                monthly_avg_df = monthly_avg_df[monthly_avg_df["category"] == selected_category]
            st.dataframe(
                monthly_avg_df,
                column_config={
                    "category": "Category",
                    "Monthly Average ($)": st.column_config.NumberColumn(
                        "Monthly Average ($)",
                        format="$%.2f"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.subheader("Monthly Finance Breakdown")
            st.dataframe(
                sum_month_finance_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Expense Amount ($)": st.column_config.NumberColumn(
                        "Expense Amount ($)", format="$%.2f"
                    ),
                    "Income Amount ($)": st.column_config.NumberColumn(
                        "Income Amount ($)", format="$%.2f"
                    ),
                },
            )


dashboard()
