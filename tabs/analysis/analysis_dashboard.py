import streamlit as st

from tabs.analysis.analysis_agents import expense_agent
from utils.ai_utils import stream_llm_output

st.title("Financial Analysis")

model = st.selectbox("Select a model", ["smollm2:1.7b-instruct-q8_0", "gemma3:4b-it-q8_0"])

e = expense_agent(model)

st.write(e.run("How much money did I spend on the month of January?"))

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