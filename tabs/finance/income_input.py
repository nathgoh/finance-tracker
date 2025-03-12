import pandas as pd
import streamlit as st

from datetime import datetime

from utils.income_utils import get_incomes_df, save_income_data, delete_income_data
from utils.session_state_utils import init_income_session_state


def income_form():
    """
    Renders a form for adding a new income. The form contains fields for:
    - income amount
    - category selection
    - date selection
    - notes text input

    When the form is submitted, the add_income function is called with the
    form values as arguments. If the form is submitted successfully,
    a success message is displayed.
    """

    st.subheader("Add a New Income")
    with st.form("income_form", clear_on_submit=True):
        income = st.number_input(
            "Income", value=None, placeholder="Enter income amount...", format="%.2f"
        )
        date = st.date_input("Date", datetime.now())
        source = st.text_input("Source")
        submit = st.form_submit_button("Add Income")

    if submit:
        if income is None:
            st.error("Income amount is required!")
        else:
            add_income(income, date, source)


def add_income(amount, date, source):
    """
    Adds a new income to the session state.

    Parameters:
        amount (float): The income amount.
        date (datetime): The date of the income.
        source (str): Source of the income.
    """

    income = {
        "Amount": amount,
        "Date": date.strftime("%Y-%m-%d"),
        "Source": source,
    }
    st.session_state.incomes.append(income)
    save_income_data()


def get_monthly_breakdown():
    """
    Gets a DataFrame with monthly breakdown of incomes.
    """

    st.divider()
    st.subheader("Monthly Breakdown")

    income_df = get_incomes_df()
    if not income_df.empty:
        income_df["date"] = pd.to_datetime(income_df["date"])
        income_df["month"] = income_df["date"].dt.month_name()
        income_df["year"] = income_df["date"].dt.year

        # Group by year and month and calculate summaries
        monthly_breakdown = (
            income_df.groupby(["year", "month"])
            .agg({"amount": ["sum", "count", "mean"]})
            .round(2)
        )

        # Flatten column names
        monthly_breakdown.columns = ["Total ($)", "Number of Incomes", "Average ($)"]
        monthly_breakdown.sort_index(ascending=[False, False])

        years = sorted(income_df["year"].unique(), reverse=True)
        year_select = st.selectbox("Select Year", years, index=0)
        if year_select:
            current_month = datetime.now().strftime("%B")
            year_data = monthly_breakdown.loc[year_select]
            months = sorted(year_data.index.tolist(), key=MONTHS_MAP.get)
            month_idx = next(
                (i for i, m in enumerate(months) if m == current_month),
                months.index(months[0]) if months else 0,
            )
            month_select = st.selectbox("Select Month", months, index=month_idx)
            if month_select:
                breakdown = year_data.loc[month_select]
                total, num_expense, avg = st.columns(3)

                with total:
                    st.metric("Total ($)", breakdown["Total ($)"])
                with num_expense:
                    st.metric("Number of Incomes", breakdown["Number of Incomes"])
                with avg:
                    st.metric("Average ($)", breakdown["Average ($)"])

                month_income_df = get_incomes_df(
                    f"{year_select}-{datetime.strptime(month_select, '%B').month:02d}"
                )
                st.data_editor(
                    month_income_df,
                    key="edited_month_income",
                    num_rows="dynamic",
                    use_container_width=True,
                    column_order=["amount", "date", "source"],
                    column_config={
                        "amount": st.column_config.NumberColumn(
                            "Amount ($)", format="$%.2f"
                        ),
                        "date": st.column_config.TextColumn("Date"),
                        "source": st.column_config.TextColumn("Source"),
                    },
                    hide_index=True,
                )

                if st.session_state.edited_month_income.get("deleted_rows") is not None:
                    rows_to_delete = st.session_state.edited_month_income.get(
                        "deleted_rows"
                    )
                    ids_to_delete = [
                        int(month_income_df.iloc[i].id) for i in rows_to_delete
                    ]
                    delete_income_data(ids_to_delete)
                    st.session_state.edited_month_income["deleted_rows"] = None
                    st.rerun()


def income_input_page():
    """
    Renders a Streamlit page for adding and managing incomes.
    """

    init_income_session_state()
    income_form()
    get_monthly_breakdown()


income_input_page()
