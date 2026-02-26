import json

import pandas as pd

from smolagents import tool

from resources.constants import MONTHS_MAP
from utils.json_utils import read_json


def _load_expenses_df() -> pd.DataFrame:
    data = read_json("expenses.json")
    records = data.get("records", [])
    if not records:
        return pd.DataFrame(
            columns=["id", "amount", "category", "date", "notes",
                      "frequency", "recurring_id"]
        )
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _resolve_month(month_input: str) -> int:
    month_input = month_input.strip()

    if month_input.isdigit():
        m = int(month_input)
        if 1 <= m <= 12:
            return m
        raise ValueError(f"Month number must be 1-12, got {m}")

    for name, num in MONTHS_MAP.items():
        if name.lower().startswith(month_input.lower()):
            return num

    raise ValueError(
        f"Could not resolve month '{month_input}'. "
        f"Use a name (January, jan) or number (1-12)."
    )


@tool
def get_expense_categories() -> str:
    """Returns all valid expense category names.

    Returns:
        str: JSON list of category names.
    """
    categories = read_json("categories.json")
    return json.dumps({"categories": categories or []})


@tool
def get_monthly_expenses(year: str, month: str) -> str:
    """Returns the total expenses, transaction count, and per-category breakdown
    for a specific month.

    Args:
        year: The year to query (e.g. "2025").
        month: The month to query (e.g. "January", "jan", or "1").

    Returns:
        str: JSON expense summary for the month.
    """
    df = _load_expenses_df()
    if df.empty:
        return json.dumps({"error": "No expense data found."})

    y = int(year)
    m = _resolve_month(month)
    month_name = [k for k, v in MONTHS_MAP.items() if v == m][0]

    filtered = df[(df["date"].dt.year == y) & (df["date"].dt.month == m)]
    if filtered.empty:
        return json.dumps({"error": f"No expenses found for {month_name} {y}."})

    total = float(filtered["amount"].sum())
    count = len(filtered)
    by_cat = (
        filtered.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    result = {
        "period": f"{month_name} {y}",
        "total": round(total, 2),
        "transaction_count": count,
        "by_category": {cat: round(float(amt), 2) for cat, amt in by_cat.items()},
    }
    return json.dumps(result)


@tool
def get_category_expenses(category: str, year: str = "") -> str:
    """Returns total and monthly breakdown of expenses for a specific category.

    Args:
        category: The expense category name (e.g. "Grocery").
        year: Optional year to filter by (e.g. "2025"). If empty, includes all years.

    Returns:
        str: JSON category expense breakdown.
    """
    df = _load_expenses_df()
    if df.empty:
        return json.dumps({"error": "No expense data found."})

    filtered = df[df["category"].str.lower() == category.strip().lower()]
    if year:
        filtered = filtered[filtered["date"].dt.year == int(year)]

    if filtered.empty:
        scope = f" in {year}" if year else ""
        return json.dumps({"error": f"No expenses found for category '{category}'{scope}."})

    total = float(filtered["amount"].sum())
    count = len(filtered)

    filtered = filtered.copy()
    filtered["month_label"] = filtered["date"].dt.strftime("%B %Y")
    filtered["sort_key"] = filtered["date"].dt.to_period("M")
    by_month = (
        filtered.groupby(["sort_key", "month_label"])["amount"]
        .sum()
        .reset_index()
        .sort_values("sort_key")
    )

    result = {
        "category": category,
        "year": year or "all",
        "total": round(total, 2),
        "transaction_count": count,
        "by_month": [
            {"month": row["month_label"], "amount": round(float(row["amount"]), 2)}
            for _, row in by_month.iterrows()
        ],
    }
    return json.dumps(result)


@tool
def get_top_expenses(year: str, month: str = "", limit: str = "5") -> str:
    """Returns the top N largest individual expenses.

    Args:
        year: The year to query (e.g. "2025").
        month: Optional month to filter by (e.g. "January", "jan", or "1").
        limit: Number of top expenses to return (default "5").

    Returns:
        str: JSON list of top expenses with details.
    """
    expenses_df = _load_expenses_df()
    if expenses_df.empty:
        return json.dumps({"error": "No expense data found."})

    y = int(year)
    n = int(limit)
    filtered = expenses_df[expenses_df["date"].dt.year == y]

    period = str(y)
    if month:
        m = _resolve_month(month)
        month_name = [k for k, v in MONTHS_MAP.items() if v == m][0]
        filtered = filtered[filtered["date"].dt.month == m]
        period = f"{month_name} {y}"

    if filtered.empty:
        return json.dumps({"error": f"No expenses found for {period}."})

    top = filtered.nlargest(n, "amount")

    expenses = []
    for _, row in top.iterrows():
        entry = {
            "amount": round(float(row["amount"]), 2),
            "category": row["category"],
            "date": row["date"].strftime("%Y-%m-%d"),
        }
        if row.get("notes"):
            entry["notes"] = row["notes"]
        expenses.append(entry)

    result = {
        "period": period,
        "limit": n,
        "expenses": expenses,
    }
    return json.dumps(result)


@tool
def get_recurring_expenses(year: str = "") -> str:
    """Returns recurring expense groups with their frequency, total amount,
    and date range.

    Args:
        year: Optional year to filter by (e.g. "2025"). If empty, includes all.

    Returns:
        str: JSON list of recurring expense groups.
    """
    expenses_df = _load_expenses_df()
    if expenses_df.empty:
        return json.dumps({"error": "No expense data found."})

    recurring = expenses_df[expenses_df["recurring_id"].notna() & (expenses_df["recurring_id"] != "")]
    if year:
        recurring = recurring[recurring["date"].dt.year == int(year)]

    if recurring.empty:
        scope = f" in {year}" if year else ""
        return json.dumps({"error": f"No recurring expenses found{scope}."})

    groups = []
    for rid, group in recurring.groupby("recurring_id"):
        group_sorted = group.sort_values("date")
        cat = group_sorted.iloc[0]["category"]
        freq = group_sorted.iloc[0].get("frequency", "Unknown")
        total = float(group_sorted["amount"].sum())
        avg = float(group_sorted["amount"].mean())
        count = len(group_sorted)
        first = group_sorted["date"].min().strftime("%Y-%m-%d")
        last = group_sorted["date"].max().strftime("%Y-%m-%d")
        note = group_sorted.iloc[0].get("notes", "")

        groups.append({
            "recurring_id": rid,
            "label": note if note else cat,
            "category": cat,
            "frequency": freq,
            "occurrences": count,
            "total": round(total, 2),
            "average": round(avg, 2),
            "first_date": first,
            "last_date": last,
        })

    result = {
        "year": year or "all",
        "recurring_expenses": groups,
    }
    return json.dumps(result)
