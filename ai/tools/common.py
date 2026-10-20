import difflib
import re

import pandas as pd

from resources.constants import MONTHS_MAP
from utils.json_utils import read_json

EXPENSE_COLUMNS = [
    "id",
    "amount",
    "category",
    "date",
    "notes",
    "frequency",
    "recurring_id",
]
INCOME_COLUMNS = ["id", "amount", "date", "source"]


def load_expenses_df() -> pd.DataFrame:
    records = read_json("expenses.json").get("records", [])
    if not records:
        return pd.DataFrame(columns=pd.Index(EXPENSE_COLUMNS))
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_incomes_df() -> pd.DataFrame:
    records = read_json("incomes.json").get("records", [])
    if not records:
        return pd.DataFrame(columns=pd.Index(INCOME_COLUMNS))
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


def list_years() -> list[str]:
    years = set()
    for filename in ("expenses.json", "incomes.json"):
        for record in read_json(filename).get("records", []):
            years.add(record["date"][:4])
    return sorted(years)


def list_categories() -> list[str]:
    return read_json("categories.json") or []


def resolve_month(month_input: str) -> int:
    month_input = str(month_input).strip()

    # Models often send a date like "2024-10" or "2024-10-15" instead of a month
    date_match = re.fullmatch(r"\d{4}-(\d{1,2})(?:-\d{1,2})?", month_input)
    if date_match:
        month_input = date_match.group(1)

    if month_input.isdigit():
        m = int(month_input)
        if 1 <= m <= 12:
            return m
        raise ValueError(f"Month number must be 1-12, got {m}.")

    if month_input:
        for name, num in MONTHS_MAP.items():
            if name.lower().startswith(month_input.lower()):
                return num

    raise ValueError(
        f"Could not resolve month '{month_input}'. Use a name (January, jan) or number (1-12)."
    )


def month_name(month_num: int) -> str:
    return next(k for k, v in MONTHS_MAP.items() if v == month_num)


def resolve_category(category: str) -> str:
    """
    Maps a loosely written category (e.g. "groceries") to the exact stored name.
    """
    categories = list_categories()
    wanted = str(category).strip().lower()
    by_lower = {c.lower(): c for c in categories}

    if wanted in by_lower:
        return by_lower[wanted]

    close = difflib.get_close_matches(wanted, list(by_lower), n=1, cutoff=0.6)
    if close:
        return by_lower[close[0]]

    raise ValueError(
        f"Unknown category '{category}'. Valid categories: {', '.join(categories)}."
    )


def filter_period(
    df: pd.DataFrame, year: int, month: str = ""
) -> tuple[pd.DataFrame, str]:
    """
    Filters a dataframe to a year, and optionally a month. Returns the rows and a label.
    """
    if df.empty:
        return df, str(year)

    filtered = df[df["date"].dt.year == year]
    label = str(year)

    if month:
        m = resolve_month(month)
        filtered = filtered[filtered["date"].dt.month == m]
        label = f"{month_name(m)} {year}"

    return filtered, label
