import streamlit as st
import pandas as pd

from components.expense_form import expense_form

st.title("Finance Tracker")
expense_form()
