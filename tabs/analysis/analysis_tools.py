# @tool
# def expense_table_engine(query: str) -> str:
#     """
#     Allows you to perform SQL queries on the table. Returns a string representation of the result.
#     The table name is "expenses". Its description is as follows:
#         Columns:
#            - id INTEGER
#            - amount REAL
#            - category TEXT
#            - date TEXT
#            - notes TEXT
#            - frequency TEXT
#            - recurring_id TEXT
#         Do note that date is in the format YYYY-MM-DD
#     Args:
#         query: The query to perform. This should be correct SQL.
#     """

#     output = ""
#     engine = create_engine(f"sqlite:///{get_database_path(DB_FILE)}")
#     with engine.connect() as conn:
#         rows = conn.execute(text(query))
#         for row in rows:
#             output += "\n" + str(row)
#     return output
