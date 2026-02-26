from ai.tools.date_tools import current_date, list_available_years
from ai.tools.expense_tools import (
    get_category_expenses,
    get_expense_categories,
    get_monthly_expenses,
    get_recurring_expenses,
    get_top_expenses,
)
from ai.tools.income_tools import get_income_sources, get_monthly_income
from ai.tools.summary_tools import (
    compare_months,
    get_average_monthly_spending,
    get_financial_summary,
    get_spending_trend,
)

ALL_TOOLS = [
    current_date,
    list_available_years,
    get_expense_categories,
    get_monthly_expenses,
    get_category_expenses,
    get_top_expenses,
    get_recurring_expenses,
    get_monthly_income,
    get_income_sources,
    get_financial_summary,
    compare_months,
    get_spending_trend,
    get_average_monthly_spending,
]
