
import streamlit as st

from db import query_database
from agent import make_agent, invoke_agent


if "agent" not in st.session_state:
    st.session_state["agent"] = make_agent()
agent = st.session_state["agent"]

st.title("Conversational Analytics at Home")

prompt = st.chat_input("Ask me anything about NBA stats.")

if prompt:
    st.text(prompt)
    with st.spinner("Generating response..."):
        resp = invoke_agent(agent, prompt)

        data = query_database(resp.sql)
        exec(resp.python, {}, {"query_result": data})

        with st.expander("Generated SQL"):
            st.code(resp.sql, language='sql')

        with st.expander("Generated Python"):
            st.code(resp.python, language='python')
