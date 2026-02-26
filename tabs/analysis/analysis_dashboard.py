import streamlit as st

from ai.agent import get_agent
from resources.constants import LLM_MODELS

st.title("Financial Analysis")

with st.sidebar:
    model = st.selectbox("Model", list(LLM_MODELS.keys()))

    if st.button("New Conversation"):
        agent = get_agent(model)
        agent.memory.reset()
        st.session_state.chat_messages = []
        st.rerun()

# Reset chat when model changes
if st.session_state.get("current_model") != model:
    st.session_state.current_model = model
    st.session_state.chat_messages = []
    get_agent(model).memory.reset()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if query := st.chat_input("Ask about your finances..."):
    st.session_state.chat_messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    agent = get_agent(model)
    is_first_message = len(st.session_state.chat_messages) == 1

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = agent.run(task=query, reset=is_first_message)
        st.markdown(response)

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": response}
    )
