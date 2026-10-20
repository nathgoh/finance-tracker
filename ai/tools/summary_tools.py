import json

from smolagents import tool

from ai.tools.common import (
    filter_period,
    load_expenses_df,
    load_incomes_df,
    month_name,
    resolve_category,
    resolve_month,
)


@tool
def get_financial_summary(year: int, month: str = "") -> str:
    """Overview of income, expenses, savings, savings rate, and spending by category
    for a year or a single month.

    Args:
        year: The year to query (e.g. 2025).
        month: A month name or number 1-12 (e.g. "March" or "3"), never a date. Leave empty for the whole year.

    Returns:
        str: JSON financial summary.
    """
    expenses, period = filter_period(load_expenses_df(), year, month)
    incomes, _ = filter_period(load_incomes_df(), year, month)
    if expenses.empty and incomes.empty:
        return json.dumps({"error": f"No income or expenses found for {period}."})

    total_income = float(incomes["amount"].sum())
    total_expenses = float(expenses["amount"].sum())
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0.0

    expense_breakdown = {}
    if not expenses.empty:
        by_cat = (
            expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
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
        "transaction_count": len(expenses),
        "savings": round(savings, 2),
        "savings_rate": round(savings_rate, 1),
        "expense_breakdown": expense_breakdown,
    }
    return json.dumps(result)


@tool
def compare_months(year: int, month_1: str, month_2: str) -> str:
    """Compare income, expenses, savings, and per-category spending between two months
    of the same year.

    Args:
        year: The year (e.g. 2025).
        month_1: First month (e.g. "January", "jan", or "1").
        month_2: Second month (e.g. "February", "feb", or "2").

    Returns:
        str: JSON comparison with deltas.
    """
    expenses_df = load_expenses_df()
    incomes_df = load_incomes_df()
    first = resolve_month(month_1)
    second = resolve_month(month_2)
    first_name = month_name(first)
    second_name = month_name(second)

    def month_totals(df, month_num, group_col=None):
        if df.empty:
            return 0.0, {}
        filtered = df[(df["date"].dt.year == year) & (df["date"].dt.month == month_num)]
        breakdown = {}
        if group_col and not filtered.empty:
            breakdown = {
                k: round(float(v), 2)
                for k, v in filtered.groupby(group_col)["amount"].sum().items()
            }
        return float(filtered["amount"].sum()), breakdown

    expense_1, category_1 = month_totals(expenses_df, first, group_col="category")
    expense_2, category_2 = month_totals(expenses_df, second, group_col="category")
    income_1, _ = month_totals(incomes_df, first)
    income_2, _ = month_totals(incomes_df, second)

    category_comparison = {}
    for cat in sorted(set(category_1) | set(category_2)):
        a = category_1.get(cat, 0.0)
        b = category_2.get(cat, 0.0)
        category_comparison[cat] = {
            first_name: round(a, 2),
            second_name: round(b, 2),
            "delta": round(b - a, 2),
        }

    def compare(a: float, b: float) -> dict:
        return {
            first_name: round(a, 2),
            second_name: round(b, 2),
            "delta": round(b - a, 2),
        }

    result = {
        "year": year,
        "income": compare(income_1, income_2),
        "expenses": compare(expense_1, expense_2),
        "savings": compare(income_1 - expense_1, income_2 - expense_2),
        "category_breakdown": category_comparison,
    }
    return json.dumps(result)


@tool
def get_spending_trend(year: int, category: str = "") -> str:
    """Month-by-month spending for a year with month-over-month change, plus the
    total and average monthly spending.

    Args:
        year: The year to query (e.g. 2025).
        category: Category to filter by (e.g. "Grocery"). Leave empty for all spending.

    Returns:
        str: JSON monthly trend, total, and average per month.
    """
    df = load_expenses_df()
    if df.empty:
        return json.dumps({"error": "No expense data found."})

    filtered = df[df["date"].dt.year == year]
    if category:
        category = resolve_category(category)
        filtered = filtered[filtered["category"] == category]

    if filtered.empty:
        scope = f" for '{category}'" if category else ""
        return json.dumps({"error": f"No expenses found{scope} in {year}."})

    monthly = filtered.groupby(filtered["date"].dt.month)["amount"].sum().sort_index()

    months = []
    prev = None
    for month_num, amount in monthly.items():
        amount = round(float(amount), 2)
        entry = {"month": month_name(month_num), "amount": amount}
        if prev:
            entry["mom_change_percent"] = round((amount - prev) / prev * 100, 1)
        prev = amount
        months.append(entry)

    result = {
        "year": year,
        "category": category or "all",
        "months": months,
        "total": round(float(monthly.sum()), 2),
        "average_per_month": round(float(monthly.mean()), 2),
    }
    return json.dumps(result)
