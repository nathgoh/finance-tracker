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
def get_financial_summary(year: str, month: str = "") -> str:
    """Returns a financial overview with income, expenses, savings, savings rate,
    and expense breakdown by category.

    Args:
        year: The year to query, use current_date tool to find today's date.
        month: Optional month to filter by (e.g. "January", "jan", or "1").

    Returns:
        str: JSON financial summary.
    """
    exp_df = _load_expenses_df()
    inc_df = _load_incomes_df()

    y = int(year)
    period = str(y)

    if not exp_df.empty:
        exp_filtered = exp_df[exp_df["date"].dt.year == y]
    else:
        exp_filtered = exp_df

    if not inc_df.empty:
        inc_filtered = inc_df[inc_df["date"].dt.year == y]
    else:
        inc_filtered = inc_df

    if month:
        m = _resolve_month(month)
        month_name = [k for k, v in MONTHS_MAP.items() if v == m][0]
        period = f"{month_name} {y}"
        if not exp_filtered.empty:
            exp_filtered = exp_filtered[exp_filtered["date"].dt.month == m]
        if not inc_filtered.empty:
            inc_filtered = inc_filtered[inc_filtered["date"].dt.month == m]

    total_income = float(inc_filtered["amount"].sum() if not inc_filtered.empty else 0)
    total_expenses = float(exp_filtered["amount"].sum() if not exp_filtered.empty else 0)
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0.0

    expense_breakdown = {}
    if not exp_filtered.empty:
        by_cat = (
            exp_filtered.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )
        for cat, amt in by_cat.items():
            pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
            expense_breakdown[cat] = {
                "amount": round(float(amt), 2),
                "percentage": round(float(pct), 1),
            }

    result = {
        "period": period,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "savings": round(savings, 2),
        "savings_rate": round(savings_rate, 1),
        "expense_breakdown": expense_breakdown,
    }

    return json.dumps(result)


@tool
def compare_months(year: str, month_1: str, month_2: str) -> str:
    """Compares income, expenses, and per-category spending between two months
    in the same year.

    Args:
        year: The year (e.g. "2025").
        month_1: First month (e.g. "January", "jan", or "1").
        month_2: Second month (e.g. "February", "feb", or "2").

    Returns:
        str: JSON comparison with deltas.
    """
    expenses_df = _load_expenses_df()
    incomes_df = _load_incomes_df()
    y = int(year)
    first_month = _resolve_month(month_1)
    second_month = _resolve_month(month_2)
    first_month_name = [k for k, v in MONTHS_MAP.items() if v == first_month][0]
    second_month_name = [k for k, v in MONTHS_MAP.items() if v == second_month][0]

    def _month_totals(df, month_num, amount_col="amount", group_col=None):
        if df.empty:
            return 0.0, {}
        filtered = df[
            (df["date"].dt.year == y) & (df["date"].dt.month == month_num)
        ]
        total = float(filtered[amount_col].sum())
        breakdown = {}
        if group_col and not filtered.empty:
            breakdown = {
                k: round(float(v), 2)
                for k, v in filtered.groupby(group_col)[amount_col].sum().items()
            }
        return total, breakdown

    expense_1, category_1 = _month_totals(expenses_df, first_month, group_col="category")
    expense_2, category_2 = _month_totals(expenses_df, second_month, group_col="category")
    income_1, _ = _month_totals(incomes_df, first_month)
    income_2, _ = _month_totals(incomes_df, second_month)

    savings_1 = income_1 - expense_1
    savings_2 = income_2 - expense_2

    all_cats = sorted(set(list(category_1.keys()) + list(category_2.keys())))
    category_comparison = {}
    for cat in all_cats:
        a = category_1.get(cat, 0.0)
        b = category_2.get(cat, 0.0)
        category_comparison[cat] = {
            first_month_name: round(a, 2),
            second_month_name: round(b, 2),
            "delta": round(b - a, 2),
        }

    result = {
        "year": y,
        "month_1": first_month_name,
        "month_2": second_month_name,
        "income": {
            first_month_name: round(income_1, 2),
            second_month_name: round(income_2, 2),
            "delta": round(income_2 - income_1, 2),
        },
        "expenses": {
            first_month_name: round(expense_1, 2),
            second_month_name: round(expense_2, 2),
            "delta": round(expense_2 - expense_1, 2),
        },
        "savings": {
            first_month_name: round(savings_1, 2),
            second_month_name: round(savings_2, 2),
            "delta": round(savings_2 - savings_1, 2),
        },
        "category_breakdown": category_comparison,
    }

    return json.dumps(result)


@tool
def get_spending_trend(year: str, category: str = "") -> str:
    """Returns month-by-month spending amounts with month-over-month change
    percentages.

    Args:
        year: The year to query (e.g. "2025").
        category: Optional category to filter by. If empty, shows total spending.

    Returns:
        str: JSON monthly trend with MoM change.
    """
    expenses_df = _load_expenses_df()
    if expenses_df.empty:
        return json.dumps({"error": "No expense data found."})

    y = int(year)
    filtered = expenses_df[expenses_df["date"].dt.year == y]

    if category:
        filtered = filtered[
            filtered["category"].str.lower() == category.strip().lower()
        ]

    if filtered.empty:
        scope = f" for '{category}'" if category else ""
        return json.dumps({"error": f"No expenses found{scope} in {year}."})

    monthly = (
        filtered.groupby(filtered["date"].dt.month)["amount"]
        .sum()
        .sort_index()
    )

    months = []
    prev = None
    for month_num, amount in monthly.items():
        month_name = [k for k, v in MONTHS_MAP.items() if v == month_num][0]
        amount = round(float(amount), 2)
        entry = {"month": month_name, "amount": amount}
        if prev is not None and prev > 0:
            entry["mom_change"] = round((amount - prev) / prev * 100, 1)
        prev = amount
        months.append(entry)

    result = {
        "year": y,
        "category": category or "all",
        "months": months,
    }

    return json.dumps(result)


@tool
def get_average_monthly_spending(year: str, category: str = "") -> str:
    """Returns the average monthly spending over months that have data.

    Args:
        year: The year to query (e.g. "2025").
        category: Optional category to filter by. If empty, shows total average.

    Returns:
        str: JSON average monthly spending.
    """
    expenses_df = _load_expenses_df()
    if expenses_df.empty:
        return json.dumps({"error": "No expense data found."})

    y = int(year)
    filtered = expenses_df[expenses_df["date"].dt.year == y]

    if category:
        filtered = filtered[
            filtered["category"].str.lower() == category.strip().lower()
        ]

    if filtered.empty:
        scope = f" for '{category}'" if category else ""
        return json.dumps({"error": f"No expenses found{scope} in {year}."})

    monthly = (
        filtered.groupby(filtered["date"].dt.month)["amount"]
        .sum()
    )

    result = {
        "year": y,
        "category": category or "all",
        "average_monthly_spending": round(float(monthly.mean()), 2),
        "total_spending": round(float(monthly.sum()), 2),
        "num_months": len(monthly),
    }

    return json.dumps(result)
