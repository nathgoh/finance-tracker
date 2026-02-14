import pandas as pd
import streamlit as st

from datetime import datetime

from utils.json_utils import read_json, write_json


def get_incomes_df(date=str(datetime.now().year)) -> pd.DataFrame:
    """
    Gets a DataFrame of incomes from the JSON data store.

    Returns a DataFrame containing incomes filtered by date prefix.
    """

    data = read_json("incomes.json")
    df = pd.DataFrame(data["records"])

    if df.empty:
        return pd.DataFrame(columns=["id", "amount", "date", "source"])

    df = df[df["date"].str.startswith(str(date))]
    return df[["id", "amount", "date", "source"]]


def save_income_data():
    """
    Save income data to the JSON data store.
    """

    try:
        data = read_json("incomes.json")
        new_income = st.session_state.incomes[-1]

        record = {
            "id": data["next_id"],
            "amount": new_income["Amount"],
            "date": new_income["Date"],
            "source": new_income["Source"],
        }
        data["records"].append(record)
        data["next_id"] += 1
        write_json("incomes.json", data)
    except Exception as e:
        st.error(f"Failed to saving income input data: {e}")


def delete_income_data(income_ids: list):
    """
    Delete incomes from the data store based on their primary key values.
    """

    if not income_ids:
        return

    try:
        data = read_json("incomes.json")
        ids_set = set(income_ids)
        data["records"] = [r for r in data["records"] if r["id"] not in ids_set]
        write_json("incomes.json", data)
        st.success("Income(s) deleted successfully!")
    except Exception as e:
        st.error(f"Failed to delete income data: {e}")
