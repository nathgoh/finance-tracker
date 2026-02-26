import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent

import streamlit as st

from ai.prompts import FINANCIAL_AGENT_INSTRUCTIONS
from ai.tools import ALL_TOOLS
from resources.constants import LLM_MODELS

load_dotenv()

OLLAMA_OPENAI_ENDPOINT = os.getenv("OLLAMA_OPENAI_ENDPOINT")

@st.cache_resource
def get_agent(model_name: str) -> ToolCallingAgent:
    model = OpenAIServerModel(
        model_id=LLM_MODELS[model_name],
        api_base=OLLAMA_OPENAI_ENDPOINT,
        api_key="ollama",
        temperature=0.3,
    )

    return ToolCallingAgent(
        tools=ALL_TOOLS,
        model=model,
        instructions=FINANCIAL_AGENT_INSTRUCTIONS,
        max_steps=6,
    )
