import streamlit as st

from resources.constants import DB_FILE
from utils.db_utils import get_table_schema
from tabs.analysis.analysis_agents import expense_agent

st.title("Financial Analysis")

model = st.selectbox(
    "Select a model",
    [
        "llama3.2:3b-instruct-q8_0",
        "hengwen/watt-tool-8B",
        "llama3-groq-tool-use:8b",
        "gemini 2.0 flash lite",
    ],
)

e = expense_agent(model)
st.write(get_table_schema(DB_FILE, "expenses"))

if st.button("run"):
    st.write(
        e.run(
            (
                """
                You are a financial analysis assistant designed to help users manage their personal finances 
                by analyzing their income and expenses. Your goal is to provide insights into spending habits, 
                track income sources, and suggest ways to optimize budgeting. You should be able to identify 
                trends, and generate summary reports or visualizations. Ensure your responses are data-driven 
                and practical, helping users make informed financial decisions. Prioritize accuracy, efficiency, 
                and user privacy in all interactions"
                                
                Answer the following user query:
                "What was the total expense for this year 2025 for the month of January?"
                """
            )
        )
    )

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("What is up?"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         response = st.write_stream(stream_llm_output(model, prompt))
#     st.session_state.messages.append({"role": "assistant", "content": response})
