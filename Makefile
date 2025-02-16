run:
	streamlit run app.py

lint:
	ruff format && ruff check --fix