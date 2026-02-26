import json

import pandas as pd

from smolagents import tool

from resources.constants import MONTHS_MAP
from utils.json_utils import read_json


def _load_incomes_df() -> pd.DataFrame:
    data = read_json("incomes.json")
    records = data.get("records", [])
    if not records:
        return pd.DataFrame(columns=["id", "amount", "date", "source"])
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
def get_monthly_income(year: str, month: str = "") -> str:
    """Returns total income and breakdown by source for a given year,
    optionally filtered to a specific month.

    Args:
        year: The year to query (e.g. "2025").
        month: Optional month to filter by (e.g. "January", "jan", or "1").

    Returns:
        str: JSON income summary.
    """
    income_df = _load_incomes_df()
    if income_df.empty:
        return json.dumps({"error": "No income data found."})

    y = int(year)
    filtered = income_df[income_df["date"].dt.year == y]

    period = str(y)
    if month:
        m = _resolve_month(month)
        month_name = [k for k, v in MONTHS_MAP.items() if v == m][0]
        filtered = filtered[filtered["date"].dt.month == m]
        period = f"{month_name} {y}"

    if filtered.empty:
        return json.dumps({"error": f"No income found for {period}."})

    total = float(filtered["amount"].sum())
    by_source = (
        filtered.groupby("source")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    result = {
        "period": period,
        "total": round(total, 2),
        "by_source": {
            (source if source else "(no source)"): round(float(amt), 2)
            for source, amt in by_source.items()
        },
    }
    return json.dumps(result)


@tool
def get_income_sources(year: str = "") -> str:
    """Returns distinct income sources with their total amounts.

    Args:
        year: Optional year to filter by (e.g. "2025"). If empty, includes all.

    Returns:
        str: JSON list of income sources and totals.
    """
    income_df = _load_incomes_df()
    if income_df.empty:
        return json.dumps({"error": "No income data found."})

    if year:
        income_df = income_df[income_df["date"].dt.year == int(year)]

    if income_df.empty:
        return json.dumps({"error": f"No income found for {year}."})

    by_source = (
        income_df.groupby("source")["amount"]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=False)
    )

    sources = []
    for source, row in by_source.iterrows():
        sources.append({
            "source": source if source else "(no source)",
            "total": round(float(row["sum"]), 2),
            "count": int(row["count"]),
        })

    result = {
        "year": year or "all",
        "sources": sources,
    }
    return json.dumps(result)
