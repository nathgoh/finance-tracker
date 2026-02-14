import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.expense_utils import get_expenses_df, get_all_expense_dates
from utils.income_utils import get_incomes_df
from resources.constants import MONTHS_MAP, CATEGORY_COLORS

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
        (grouped_category_expense_df["Amount ($)"] / total_expense) * 100
    ).round(2)

    # Sort by amount descending for better visualization
    grouped_category_expense_df = grouped_category_expense_df.sort_values(
        "Amount ($)", ascending=False
    ).reset_index(drop=True)

    # Sankey diagram for full financial flow: Income → Expenses/Savings → Categories
    categories = grouped_category_expense_df["Category"].tolist()
    amounts = grouped_category_expense_df["Amount ($)"].tolist()
    percentages = grouped_category_expense_df["Percentage"].tolist()

    # Calculate total income and savings
    total_income = income_df["amount"].sum() if not income_df.empty else 0
    total_savings = total_income - total_expense

    # Helper function to convert hex to rgba
    def hex_to_rgba(hex_color, alpha=0.6):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"

    # Build nodes and links for the Sankey diagram
    node_labels = []
    node_colors = []
    node_customdata = []
    sources = []
    targets = []
    link_values = []
    link_colors_rgba = []
    link_customdata = []

    node_index = 0

    # Add income source nodes if income data exists
    if not income_df.empty and total_income > 0:
        # Group income by source
        grouped_income = income_df.groupby("source")["amount"].sum().reset_index()
        income_sources = grouped_income["source"].tolist()
        income_amounts = grouped_income["amount"].tolist()

        # Add income source nodes
        income_source_indices = []
        for source, amt in zip(income_sources, income_amounts):
            pct = (amt / total_income * 100) if total_income > 0 else 0
            node_labels.append(f"{source}<br>${amt:,.2f}")
            node_colors.append("#2E7D32")  # Green for income sources
            node_customdata.append([source, amt, pct, total_income])
            income_source_indices.append(node_index)
            node_index += 1

        # Add Total Income node
        total_income_index = node_index
        node_labels.append(f"Total Income<br>${total_income:,.2f}")
        node_colors.append("#1B5E20")  # Dark green for total income
        node_customdata.append(["Total Income", total_income, 100.0, total_income])
        node_index += 1

        # Links from income sources to Total Income
        for idx, amt in zip(income_source_indices, income_amounts):
            sources.append(idx)
            targets.append(total_income_index)
            link_values.append(amt)
            link_colors_rgba.append(hex_to_rgba("#4CAF50"))
            pct = (amt / total_income * 100) if total_income > 0 else 0
            link_customdata.append([income_sources[income_source_indices.index(idx)], amt, pct])

        # Add Expenses node
        expenses_index = node_index
        node_labels.append(f"Expenses<br>${total_expense:,.2f}")
        node_colors.append("#808080")  # Grey for expenses
        expense_pct = (total_expense / total_income * 100) if total_income > 0 else 100
        node_customdata.append(["Total Expenses", total_expense, expense_pct, total_income])
        node_index += 1

        # Link from Total Income to Expenses
        sources.append(total_income_index)
        targets.append(expenses_index)
        link_values.append(total_expense)
        link_colors_rgba.append(hex_to_rgba("#808080"))
        link_customdata.append(["Expenses", total_expense, expense_pct])

        # Add Savings node if there are savings
        if total_savings > 0:
            savings_index = node_index
            savings_pct = (total_savings / total_income * 100) if total_income > 0 else 0
            node_labels.append(f"Savings<br>${total_savings:,.2f} ({savings_pct:.1f}%)")
            node_colors.append("#1976D2")  # Blue for savings
            node_customdata.append(["Savings", total_savings, savings_pct, total_income])
            node_index += 1

            # Link from Total Income to Savings
            sources.append(total_income_index)
            targets.append(savings_index)
            link_values.append(total_savings)
            link_colors_rgba.append(hex_to_rgba("#1976D2"))
            link_customdata.append(["Savings", total_savings, savings_pct])

    else:
        # No income data - just show expenses node
        expenses_index = node_index
        node_labels.append(f"Expenses<br>${total_expense:,.2f}")
        node_colors.append("#808080")
        node_customdata.append(["Total Expenses", total_expense, 100.0, total_expense])
        node_index += 1

    # Add expense category nodes and links
    for cat, amt, pct in zip(categories, amounts, percentages):
        node_labels.append(f"{cat}<br>${amt:,.2f} ({pct:.1f}%)")
        node_colors.append(CATEGORY_COLORS.get(cat, "#888888"))
        node_customdata.append([cat, amt, pct, total_expense])

        # Link from Expenses to category
        sources.append(expenses_index)
        targets.append(node_index)
        link_values.append(amt)
        link_colors_rgba.append(hex_to_rgba(CATEGORY_COLORS.get(cat, "#888888")))
        link_customdata.append([cat, amt, pct])
        node_index += 1

    category_expense_bar = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="white", width=1),
            label=node_labels,
            color=node_colors,
            customdata=node_customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Amount: $%{customdata[1]:,.2f}<br>"
                "% of Total: %{customdata[2]:.1f}%"
                "<extra></extra>"
            ),
        ),
        link=dict(
            source=sources,
            target=targets,
            value=link_values,
            color=link_colors_rgba,
            customdata=link_customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Amount: $%{customdata[1]:,.2f}<br>"
                "% of Total: %{customdata[2]:.1f}%"
                "<extra></extra>"
            ),
        ),
    )])

    category_expense_bar.update_layout(
        title="Financial Flow: Income → Expenses → Categories",
        font=dict(size=12),
        height=500,
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
    sum_month_income_df = pd.DataFrame(columns=["Date", "Income Amount ($)"])
    if not income_df.empty:
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

         # Total monthly income
        sum_month_income_df = sum_month_income_df.rename(
            columns={"Amount ($)": "Income Amount ($)"}
        )

    # Total monthly expense
    sum_month_expense_df = sum_month_expense_df.rename(
        columns={"Amount ($)": "Expense Amount ($)"}
    )
    
    # Total monthly expense and income
    sum_month_finance_df = pd.merge(
        sum_month_expense_df, sum_month_income_df, on="Date", how="outer"
    )

    return category_expense_bar, finance_chart, sum_month_finance_df, expense_df, income_df


def dashboard():
    dates = get_all_expense_dates()

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
        expense.metric(label="Total Expense", value=f"{float(total_expense):.2f}$", border=True)
        income.metric(label="Total Income", value=f"{float(total_income):.2f}$", border=True)
        savings.metric(
            label="Total Savings", value=f"{float(total_savings):.2f}$", border=True
        )
        
        # Get finance figures/charts and data
        category_expense_bar, finance_chart, sum_month_finance_df, expense_data, income_data = (
            finance_figures(income_df, expense_df)
        )
        
        # Download Expense CSV
        expense_data['date'] = pd.to_datetime(expense_data['date'])
        expense_csv = expense_data[expense_data['date'].dt.year == year_select].assign(Type='Expense').rename(
            columns={
                'category': 'Category',
                'amount': 'Amount',
                'date': 'Date',
                'notes': 'Notes'
            }
        )[['Type', 'Category', 'Amount', 'Date', 'Notes']].to_csv(index=False)
        st.sidebar.download_button(
            label="📥 Export Expense Data as CSV",
            data=expense_csv,
            file_name=f'expense_data_{year_select}.csv',
            mime='text/csv',
            help='Download all expense data as a CSV file'
        )

        # Download Income CSV
        income_data['date'] = pd.to_datetime(income_data['date'])
        income_csv = income_data[income_data['date'].dt.year == year_select].assign(Type='Income').rename(columns={'source': 'Source', 'amount': 'Amount', 'date': 'Date'})[['Type', 'Source', 'Amount', 'Date']].to_csv(index=False)
        st.sidebar.download_button(
            label="📥 Export Income Data as CSV",
            data=income_csv,
            file_name=f'income_data_{year_select}.csv',
            mime='text/csv',
            help='Download all income data as a CSV file'
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
            )
            
            st.subheader("Monthly Finance Breakdown")
            st.dataframe(
                sum_month_finance_df,
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
