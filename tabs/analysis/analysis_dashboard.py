import streamlit as st

from resources.constants import DB_FILE
from utils.db_utils import inspect_table_in_db
from tabs.analysis.analysis_agents import expense_agent

st.title("Financial Analysis")

model = st.selectbox(
    "Select a model", ["gemma3:4b-it-q8_0"]
)

e = expense_agent(model)
st.write(inspect_table_in_db(DB_FILE, "expenses"))

if st.button("run"):
    st.write(e.run("What was the total expense for the month of January for this year 2025?"))

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
