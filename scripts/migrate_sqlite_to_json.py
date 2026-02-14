"""
One-off migration script: SQLite -> JSON

Reads data from the existing SQLite database and writes it to JSON files
in the data/ directory, preserving original IDs.

Run from the project root:
    python scripts/migrate_sqlite_to_json.py
"""

import json
import os
import sqlite3
import sys

DB_PATH = os.path.join("db", "finance_tracker.db")
DATA_DIR = "data"


def write(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Nothing to migrate.")
        sys.exit(0)

    os.makedirs(DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Migrate categories
    cursor.execute("SELECT category FROM categories")
    categories = [row["category"] for row in cursor.fetchall()]
    write(os.path.join(DATA_DIR, "categories.json"), categories)
    print(f"Migrated {len(categories)} categories")

    # Migrate expenses
    cursor.execute(
        "SELECT id, amount, category, date, notes, frequency, recurring_id FROM expenses"
    )
    expense_rows = cursor.fetchall()
    max_expense_id = max((row["id"] for row in expense_rows), default=0)
    expenses = {
        "next_id": max_expense_id + 1,
        "records": [
            {
                "id": row["id"],
                "amount": row["amount"],
                "category": row["category"],
                "date": row["date"],
                "notes": row["notes"],
                "frequency": row["frequency"],
                "recurring_id": row["recurring_id"],
            }
            for row in expense_rows
        ],
    }
    write(os.path.join(DATA_DIR, "expenses.json"), expenses)
    print(f"Migrated {len(expense_rows)} expenses (next_id={max_expense_id + 1})")

    # Migrate incomes
    cursor.execute("SELECT id, amount, date, source FROM incomes")
    income_rows = cursor.fetchall()
    max_income_id = max((row["id"] for row in income_rows), default=0)
    incomes = {
        "next_id": max_income_id + 1,
        "records": [
            {
                "id": row["id"],
                "amount": row["amount"],
                "date": row["date"],
                "source": row["source"],
            }
            for row in income_rows
        ],
    }
    write(os.path.join(DATA_DIR, "incomes.json"), incomes)
    print(f"Migrated {len(income_rows)} incomes (next_id={max_income_id + 1})")

    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
