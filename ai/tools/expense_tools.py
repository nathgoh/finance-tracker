import json

from smolagents import tool

from ai.tools.common import (
    filter_period,
    load_expenses_df,
    resolve_category,
)


@tool
def get_category_expenses(category: str, year: int = 0) -> str:
    """Total and month-by-month spending for one expense category.

    Args:
        category: The category name (e.g. "Grocery").
        year: Year to filter by (e.g. 2025). Use 0 for all years.

    Returns:
        str: JSON category expense breakdown.
    """
    df = load_expenses_df()
    if df.empty:
        return json.dumps({"error": "No expense data found."})

    category = resolve_category(category)
    filtered = df[df["category"] == category]
    if year:
        filtered = filtered[filtered["date"].dt.year == year]

    if filtered.empty:
        scope = f" in {year}" if year else ""
        return json.dumps({"error": f"No expenses found for '{category}'{scope}."})

    filtered = filtered.assign(
        month_label=filtered["date"].dt.strftime("%B %Y"),
        sort_key=filtered["date"].dt.to_period("M"),
    )
    by_month = (
        filtered.groupby(["sort_key", "month_label"])["amount"]
        .sum()
        .reset_index()
        .sort_values("sort_key")
    )

    result = {
        "category": category,
        "year": year or "all",
        "total": round(float(filtered["amount"].sum()), 2),
        "transaction_count": len(filtered),
        "by_month": [
            {"month": row["month_label"], "amount": round(float(row["amount"]), 2)}
            for _, row in by_month.iterrows()
        ],
    }
    return json.dumps(result)


@tool
def get_top_expenses(year: int, month: str = "", limit: int = 5) -> str:
    """The largest individual expenses (single purchases) in a year or month.

    Args:
        year: The year to query (e.g. 2025).
        month: A month name or number 1-12 (e.g. "March" or "3"), never a date. Leave empty for the whole year.
        limit: How many expenses to return.

    Returns:
        str: JSON list of top expenses with details.
    """
    df = load_expenses_df()
    if df.empty:
        return json.dumps({"error": "No expense data found."})

    filtered, period = filter_period(df, year, month)
    if filtered.empty:
        return json.dumps({"error": f"No expenses found for {period}."})

    expenses = []
    for _, row in filtered.nlargest(limit, "amount").iterrows():
        entry = {
            "amount": round(float(row["amount"]), 2),
            "category": row["category"],
            "date": row["date"].strftime("%Y-%m-%d"),
        }
        if row.get("notes"):
            entry["notes"] = row["notes"]
        expenses.append(entry)

    return json.dumps({"period": period, "expenses": expenses})


@tool
def get_recurring_expenses(year: int = 0) -> str:
    """Recurring expenses and subscriptions, with frequency, total, and date range.

    Args:
        year: Year to filter by (e.g. 2025). Use 0 for all years.

    Returns:
        str: JSON list of recurring expense groups.
    """
    df = load_expenses_df()
    if df.empty:
        return json.dumps({"error": "No expense data found."})

    recurring = df[df["recurring_id"].notna() & (df["recurring_id"] != "")]
    if year:
        recurring = recurring[recurring["date"].dt.year == year]

    if recurring.empty:
        scope = f" in {year}" if year else ""
        return json.dumps({"error": f"No recurring expenses found{scope}."})

    groups = []
    for rid, group in recurring.groupby("recurring_id"):
        group = group.sort_values("date")
        first_row = group.iloc[0]
        note = first_row.get("notes", "")
        groups.append(
            {
                "recurring_id": rid,
                "label": note if note else first_row["category"],
                "category": first_row["category"],
                "frequency": first_row.get("frequency", "Unknown"),
                "occurrences": len(group),
                "total": round(float(group["amount"].sum()), 2),
                "average": round(float(group["amount"].mean()), 2),
                "first_date": group["date"].min().strftime("%Y-%m-%d"),
                "last_date": group["date"].max().strftime("%Y-%m-%d"),
            }
        )

    return json.dumps({"year": year or "all", "recurring_expenses": groups})
