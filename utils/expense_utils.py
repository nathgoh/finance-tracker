import pandas as pd
import streamlit as st

from utils.json_utils import read_json, write_json


def get_expenses_df(year: None | str = None) -> pd.DataFrame:
    """
    Gets a DataFrame of expenses from the JSON data store.

    Args:
        year (None | str, optional): Filter expenses by year. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame containing expenses.
    """

    data = read_json("expenses.json")
    df = pd.DataFrame(data["records"])

    if df.empty:
        return pd.DataFrame(columns=["id", "amount", "category", "date", "notes"])

    if year:
        df = df[df["date"].str.startswith(str(year))]

    return df[["id", "amount", "category", "date", "notes"]]


def get_all_expense_dates() -> pd.DataFrame:
    """
    Gets a DataFrame of all expense dates.

    Returns:
        pd.DataFrame: DataFrame with a single 'date' column.
    """

    data = read_json("expenses.json")
    df = pd.DataFrame(data["records"])

    if df.empty:
        return pd.DataFrame(columns=["date"])

    return df[["date"]]


def save_expense_data():
    """
    Save expenses data to the JSON data store.
    """

    try:
        data = read_json("expenses.json")
        categories = read_json("categories.json")

        new_expense = st.session_state.expenses[-1]

        # Add category if it doesn't exist
        if new_expense["Category"] not in categories:
            categories.append(new_expense["Category"])
            write_json("categories.json", categories)

        # Add expense record
        record = {
            "id": data["next_id"],
            "amount": new_expense["Amount"],
            "category": new_expense["Category"],
            "date": new_expense["Date"],
            "notes": new_expense["Notes"],
            "frequency": new_expense["Frequency"],
            "recurring_id": new_expense["Recurring ID"],
        }
        data["records"].append(record)
        data["next_id"] += 1
        write_json("expenses.json", data)
    except Exception as e:
        st.error(f"Failed to saving expense input data: {e}")


def delete_expense_data(expense_ids: list):
    """
    Delete expenses from the data store based on their primary key values.

    Args:
        expense_ids (list): List of expense ids to be deleted
    """

    if not expense_ids:
        return

    try:
        data = read_json("expenses.json")
        ids_set = set(expense_ids)
        data["records"] = [r for r in data["records"] if r["id"] not in ids_set]
        write_json("expenses.json", data)
        st.success("Expense(s) deleted successfully!")
    except Exception as e:
        st.error(f"Failed to delete expense data: {e}")


def manage_categories_data(
    new_category: str | None, delete_category: str | None, update_category: list | None
):
    """
    Manages the categories of expenses.

    Args:
        new_category (str | None): Potential new category to add.
        delete_category (str | None): Potential category to delete.
        update_category (str | None): Potential category to update.
    """

    try:
        categories = read_json("categories.json")
        if new_category:
            categories.append(new_category)
        elif delete_category:
            categories = [c for c in categories if c != delete_category]
        elif update_category:
            categories = [
                update_category[1] if c == update_category[0] else c
                for c in categories
            ]
        write_json("categories.json", categories)
    except Exception as e:
        st.error(f"Failed to saving category input data: {e}")
