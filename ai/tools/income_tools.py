import json

from smolagents import tool

from ai.tools.common import filter_period, load_incomes_df


@tool
def get_income_sources(year: int, month: str = "") -> str:
    """Total income and a breakdown by source for a year or a single month.

    Args:
        year: The year to query (e.g. 2025).
        month: Month to filter by (e.g. "January", "jan", or "1"). Leave empty for the whole year.

    Returns:
        str: JSON income total and sources with totals.
    """
    df = load_incomes_df()
    if df.empty:
        return json.dumps({"error": "No income data found."})

    filtered, period = filter_period(df, year, month)
    if filtered.empty:
        return json.dumps({"error": f"No income found for {period}."})

    by_source = (
        filtered.groupby("source")["amount"]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=False)
    )

    result = {
        "period": period,
        "total": round(float(filtered["amount"].sum()), 2),
        "sources": [
            {
                "source": source if source else "(no source)",
                "total": round(float(row["sum"]), 2),
                "count": int(row["count"]),
            }
            for source, row in by_source.iterrows()
        ],
    }
    return json.dumps(result)
