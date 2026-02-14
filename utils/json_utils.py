import json
import os
import tempfile

import streamlit as st


DATA_DIR = "./data"

DEFAULT_CATEGORIES = [
    "Personal",
    "Home",
    "Health",
    "Grocery",
    "Food & Dining",
    "Entertainment",
    "Transportation",
    "Travel",
    "Miscellaneous",
]

DEFAULTS = {
    "categories.json": DEFAULT_CATEGORIES,
    "expenses.json": {"next_id": 1, "records": []},
    "incomes.json": {"next_id": 1, "records": []},
}


def get_data_dir() -> str:
    """Get the data directory path, creating it if it doesn't exist."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception as e:
        st.error(f"Failed to create data directory: {e}")
    return DATA_DIR


def get_json_path(filename: str) -> str:
    """Get the full path to a JSON data file."""
    return os.path.join(get_data_dir(), filename)


def read_json(filename: str) -> dict | list:
    """
    Read and parse a JSON data file.

    Returns sensible defaults if the file doesn't exist.
    """
    path = get_json_path(filename)
    if not os.path.exists(path):
        return DEFAULTS.get(filename, {})
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        st.error(f"Failed to read {filename}: {e}")
        return DEFAULTS.get(filename, {})


def write_json(filename: str, data: dict | list) -> None:
    """
    Atomically write data to a JSON file.

    Writes to a temp file first, then uses os.replace for atomic swap.
    """
    data_dir = get_data_dir()
    try:
        fd, tmp_path = tempfile.mkstemp(dir=data_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, get_json_path(filename))
        except Exception:
            os.unlink(tmp_path)
            raise
    except Exception as e:
        st.error(f"Failed to write {filename}: {e}")


def get_data_schema(data_name: str) -> str:
    """
    Get a human-readable schema description for the AI agent.

    Args:
        data_name: One of "expenses", "incomes", or "categories"

    Returns:
        str: Schema description string
    """
    schemas = {
        "expenses": (
            "DataFrame Schema for expenses:\n"
            "  - id: int\n"
            "  - amount: float\n"
            "  - category: str\n"
            "  - date: str (YYYY-MM-DD)\n"
            "  - notes: str (nullable)\n"
            "  - frequency: str (nullable)\n"
            "  - recurring_id: str (nullable)"
        ),
        "incomes": (
            "DataFrame Schema for incomes:\n"
            "  - id: int\n"
            "  - amount: float\n"
            "  - date: str (YYYY-MM-DD)\n"
            "  - source: str"
        ),
        "categories": "Categories: a list of category name strings",
    }
    return schemas.get(data_name, f"Unknown data: {data_name}")


def init_data_files():
    """
    Initialize JSON data files, creating defaults if they don't exist.

    Seeds default categories if categories.json is empty or missing.
    """
    for filename, default in DEFAULTS.items():
        path = get_json_path(filename)
        if not os.path.exists(path):
            write_json(filename, default)
        elif filename == "categories.json":
            categories = read_json(filename)
            if not categories:
                write_json(filename, DEFAULT_CATEGORIES)
