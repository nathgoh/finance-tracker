import streamlit as st

from tabs.analysis.analysis_agents import expense_agent

st.title("Financial Analysis")

model = st.selectbox(
    "Select a model",
    [
        "Gemini 2.0 Flash Lite",
    ],
)

expense_agent = expense_agent(model)

with st.form("financial_analysis"):
    st.write("Financial Analysis")
    user_query = st.text_area("User query")
    submit = st.form_submit_button("Submit")

prompt = f"""
    Role:
    You are an expert Financial Analysis Assistant specializing in personal finance management. 
    Your primary objective is to help users analyze their income, expenses, and overall financial health 
    with precision and actionable insights. Assume if there's no year given, that the user wants 
    financial analysis for the current year.
    
    Key Responsibilities:
        Analyze Spending Habits: Identify patterns in expenditures (e.g., recurring subscriptions, discretionary spending, essential costs).
        Track Income Sources: Categorize and monitor earnings (salary, investments, side gigs, etc.).
        Budget Optimization: Provide tailored recommendations to reduce unnecessary expenses and improve savings.
        Trend Identification: Detect long-term financial trends (e.g., increasing debt, seasonal spending spikes).
        Report Generation: Create concise summaries with key metrics (e.g., net income, savings rate, debt-to-income ratio).
                    
    Answer the following user query:
    {user_query}
"""
if submit:
    with st.spinner("Expense Agent is analyzing your query...", show_time=True):
        results = expense_agent.run(prompt)
    st.write(results)
