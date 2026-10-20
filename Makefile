run:
	uv run streamlit run app.py

lint:
	uv run ruff format && uv run ruff check --fix
