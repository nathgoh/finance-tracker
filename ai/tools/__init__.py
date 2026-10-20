from ai.tools.expense_tools import (
    get_category_expenses,
    get_recurring_expenses,
    get_top_expenses,
)
from ai.tools.income_tools import get_income_sources
from ai.tools.summary_tools import (
    compare_months,
    get_financial_summary,
    get_spending_trend,
)

ALL_TOOLS = [
    get_financial_summary,
    get_category_expenses,
    get_top_expenses,
    get_recurring_expenses,
    get_income_sources,
    compare_months,
    get_spending_trend,
]
