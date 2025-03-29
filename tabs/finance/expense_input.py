from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import sleep

import uuid
import pandas as pd
import streamlit as st
from streamlit.elements.widgets.time_widgets import DateWidgetReturn

from utils.expense_utils import (
    get_expenses_df,
    save_expense_data,
    delete_expense_data,
    manage_categories_data,
)
from utils.session_state_utils import init_expense_session_state
from resources.constants import MONTHS_MAP


def expense_form():
    """
    Renders a form for adding a new expense. The form contains fields for:
    - expense amount
    - category selection
    - date selection
    - notes text input

    When the form is submitted, the add_expense function is called with the
    form values as arguments. If the form is submitted successfully,
    a success message is displayed.
    """

    st.subheader("Add a New Expense")
    with st.form("expense_form", clear_on_submit=True):
        expense = st.number_input(
            "Expense", value=None, placeholder="Enter expense amount...", format="%.2f"
        )
        category = st.selectbox("Categories", st.session_state.categories)
        date = st.date_input("Date", datetime.now())
        notes = st.text_input("Notes")
        submit = st.form_submit_button("Add Expense")

    if submit:
        if expense is None:
            st.error("Expense amount is required!")
        else:
            add_expense(expense, category, date, notes, None, None)


def add_expense(
    amount: float,
    category: str,
    date: DateWidgetReturn,
    notes: str,
    frequency: str | None,
    recurring_id: str | None,
):
    """
    Adds a new expense to the session state.

    Args:
        amount (float): The expense amount.
        category (str): The category for the expense.
        date (DateWidgetReturn): The date of the expense.
        notes (str): Additional notes for the expense.
        frequency (str | None): The frequency if the expense is recurring, otherwise None.
        recurring_id (str | None): The recurring ID if the expense is recurring, otherwise None.

    The expense is stored as a dictionary with keys 'Amount', 'Category', 'Date', and 'Notes',
    and appended to the 'expenses' list in the session state.
    """

    expense = {
        "Amount": amount,
        "Category": category,
        "Date": date.strftime("%Y-%m-%d"),
        "Notes": notes,
        "Frequency": frequency,
        "Recurring ID": recurring_id,
    }
    st.session_state.expenses.append(expense)
    save_expense_data()


def recurring_expense_form():
    """
    Renders a form for adding a new recurring expense. The form contains fields for:
    - expense amount
    - category selection
    - start date selection
    - end date selection
    - frequency selection (weekly, biweekly, monthly, quarterly, yearly)
    - notes text input

    When the form is submitted, the add_recurring_expense function is called with the
    form values as arguments. If the form is submitted successfully,
    a success message is displayed.
    """

    st.subheader("Add a New Recurring Expense")
    with st.form("recurring_expense_form", clear_on_submit=True):
        expense = st.number_input(
            "Expense",
            value=None,
            placeholder="Enter expense amount...",
            format="%.2f",
        )
        category = st.selectbox("Category", st.session_state.categories)

        col_1, col_2 = st.columns(2)
        with col_1:
            start_date = st.date_input("Start Date")
        with col_2:
            end_date = st.date_input("End Date")
        frequency = st.selectbox(
            "Frequency",
            options=["Weekly", "Biweekly", "Monthly", "Quarterly", "Yearly"],
        )
        notes = st.text_input("Notes")
        submit = st.form_submit_button("Add Recurring Transaction")

        if submit:
            if expense is None:
                st.error("Expense amount is required!")
            else:
                recurring_id = str(uuid.uuid4())
                current_date = start_date
                frequency_delta = {
                    "Weekly": relativedelta(weeks=1),
                    "Biweekly": relativedelta(weeks=2),
                    "Monthly": relativedelta(months=1),
                    "Quarterly": relativedelta(months=3),
                    "Yearly": relativedelta(years=1),
                }

                while current_date <= end_date:
                    add_expense(
                        expense, category, current_date, notes, frequency, recurring_id
                    )
                    current_date += frequency_delta[frequency]


def manage_categories():
    """
    Manages the categories of expenses.

    This function displays a sidebar with the following components:

    1. A text input to add a new category.
    2. A button to add the new category.
    3. A list of existing categories with text inputs to edit their names.
    4. Update buttons to save the changes to each category.
    5. Delete buttons to remove each category.

    The function also handles the logic for updating and deleting categories,
    including updating the names of expenses with the same category and
    removing the category from the session state.
    """

    with st.sidebar.expander("Manage Categories"):
        # Add new category
        new_category = st.text_input("Add New Category")
        if st.button("Add Category"):
            if new_category and new_category not in st.session_state.categories:
                st.session_state.categories.append(new_category)
                manage_categories_data(new_category, None, None)
                st.success(f"Added category: {new_category}")
                sleep(0.5)
                st.rerun()
            elif new_category in st.session_state.categories:
                st.error("Category already exists!")

        st.divider()

        # Edit/Delete categories
        st.subheader("Edit Categories")
        for idx, category in enumerate(st.session_state.categories):
            with st.container():
                # Category name input
                new_category_name = st.text_input(
                    f"Category {idx + 1}", value=category, key=f"cat_{idx}"
                )

                # Update and Delete button in two columns
                col_1, col_2 = st.columns([1, 1])
                with col_1:
                    if st.button(
                        "Update", key=f"update_{idx}", use_container_width=True
                    ):
                        if new_category_name != category:
                            # Update category name in expenses
                            for expense in st.session_state.expenses:
                                if expense["category"] == category:
                                    expense["category"] = new_category_name

                            # Update category list
                            st.session_state.categories[idx] = new_category_name
                            manage_categories_data(
                                None, None, [category, new_category_name]
                            )
                            st.success(f"Updated: {category} → {new_category_name}")
                            sleep(0.5)
                            st.rerun()
                with col_2:
                    if st.button(
                        "Delete", key=f"delete_{idx}", use_container_width=True
                    ):
                        if len(st.session_state.categories) > 1:
                            df = get_expenses_df()
                            if not df.empty and (df["category"] == category).any():
                                st.error(f"Category '{category}' has expenses!")
                            else:
                                st.session_state.categories.remove(category)
                                manage_categories_data(None, category, None)
                                st.success(f"Deleted: {category}")
                                sleep(0.5)
                                st.rerun()
                        else:
                            st.error("Cannot delete last category!")


def get_monthly_breakdown():
    """
    Gets a DataFrame with monthly breakdown of expenses.
    """

    st.divider()
    st.subheader("Monthly Breakdown")

    expense_df = get_expenses_df()
    if not expense_df.empty:
        expense_df["date"] = pd.to_datetime(expense_df["date"])
        expense_df["month"] = expense_df["date"].dt.month_name()
        expense_df["year"] = expense_df["date"].dt.year

        # Group by year and month and calculate summaries
        monthly_breakdown = (
            expense_df.groupby(["year", "month"])
            .agg({"amount": ["sum", "count", "mean"]})
            .round(2)
        )

        # Flatten column names
        monthly_breakdown.columns = ["Total ($)", "Number of Expenses", "Average ($)"]
        monthly_breakdown.sort_index(ascending=[False, False])

        years = sorted(expense_df["year"].unique(), reverse=True)
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
                    st.metric("Number of Expenses", breakdown["Number of Expenses"])
                with avg:
                    st.metric("Average ($)", breakdown["Average ($)"])

                month_expense_df = get_expenses_df(
                    f"{year_select}-{datetime.strptime(month_select, '%B').month:02d}"
                )

                st.data_editor(
                    month_expense_df,
                    key="edited_month_expense",
                    num_rows="dynamic",
                    use_container_width=True,
                    column_order=["date", "category", "amount", "notes"],
                    column_config={
                        "amount": st.column_config.NumberColumn(
                            "Amount ($)", format="$%.2f"
                        ),
                        "category": st.column_config.TextColumn("Category"),
                        "date": st.column_config.TextColumn("Date"),
                        "notes": st.column_config.TextColumn("Notes"),
                    },
                    hide_index=True,
                )

                if (
                    st.session_state.edited_month_expense.get("deleted_rows")
                    is not None
                ):
                    rows_to_delete = st.session_state.edited_month_expense.get(
                        "deleted_rows"
                    )
                    ids_to_delete = [
                        int(month_expense_df.iloc[i].id) for i in rows_to_delete
                    ]
                    delete_expense_data(ids_to_delete)
                    st.session_state.edited_month_expense["deleted_rows"] = None
                    st.rerun()


def expense_input_page():
    """
    Renders a Streamlit page for adding and managing expenses.
    """

    init_expense_session_state()
    manage_categories()

    single_expense, recurring_expense = st.tabs(
        ["New Expense", "New Recurring Expense"]
    )
    with single_expense:
        expense_form()
    with recurring_expense:
        recurring_expense_form()
    get_monthly_breakdown()


expense_input_page()
