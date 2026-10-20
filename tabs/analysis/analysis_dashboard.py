from concurrent.futures import Future, ThreadPoolExecutor

import streamlit as st

from ai.agent import get_agent
from resources.constants import LLM_MODELS


@st.cache_resource
def get_executor() -> ThreadPoolExecutor:
    # The agent (and its memory) is shared across sessions, so only run one query at a time
    return ThreadPoolExecutor(max_workers=1)


def run_agent(model: str, query: str, reset: bool) -> str:
    # Runs in a worker thread, so it must not touch st.session_state or render anything
    return get_agent(model).run(task=query, reset=reset)


@st.fragment(run_every=2)
def poll_pending_response():
    """
    Polls the background agent run and, once it finishes, moves the answer into the chat history.
    """
    future: Future = st.session_state.pending_response
    if future.done():
        error = future.exception()
        content = (
            f"Sorry, the analysis failed: {error}" if error else str(future.result())
        )
        st.session_state.chat_messages.append({"role": "assistant", "content": content})
        st.session_state.pending_response = None
        st.rerun()
    else:
        with st.chat_message("assistant"):
            st.markdown("_Analyzing..._")


st.title("Financial Analysis")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "pending_response" not in st.session_state:
    st.session_state.pending_response = None

is_running = st.session_state.pending_response is not None

with st.sidebar:
    model = st.selectbox("Model", list(LLM_MODELS.keys()), disabled=is_running)

    if st.button("New Conversation", disabled=is_running):
        agent = get_agent(model)
        agent.memory.reset()
        st.session_state.chat_messages = []
        st.rerun()

# Reset chat when model changes
if st.session_state.get("current_model") != model:
    st.session_state.current_model = model
    st.session_state.chat_messages = []
    get_agent(model).memory.reset()

# Chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if query := st.chat_input("Ask about your finances...", disabled=is_running):
    st.session_state.chat_messages.append({"role": "user", "content": query})
    is_first_message = len(st.session_state.chat_messages) == 1
    # Run in the background so the answer is kept if the user leaves this page
    st.session_state.pending_response = get_executor().submit(
        run_agent, model, query, is_first_message
    )
    st.rerun()

if st.session_state.pending_response is not None:
    poll_pending_response()
