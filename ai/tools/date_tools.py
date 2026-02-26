import json
from datetime import datetime

from smolagents import tool

from utils.json_utils import read_json


@tool
def current_date() -> str:
    """Returns today's date along with the current year and month name.

    Returns:
        str: JSON with today's date, year, and month.
    """
    today = datetime.today()
    result = {
        "date": today.strftime("%Y-%m-%d"),
        "year": today.year,
        "month": today.strftime("%B"),
    }
    return json.dumps(result)


@tool
def list_available_years() -> str:
    """Lists all years that have financial data (expenses or incomes).

    Returns:
        str: JSON list of years with data.
    """
    years = set()

    expenses = read_json("expenses.json")
    for r in expenses.get("records", []):
        years.add(r["date"][:4])

    incomes = read_json("incomes.json")
    for r in incomes.get("records", []):
        years.add(r["date"][:4])

    if not years:
        return json.dumps({"years": []})

    return json.dumps({"years": sorted(years)})
