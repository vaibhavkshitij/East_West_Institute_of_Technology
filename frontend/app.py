import streamlit as st
import sys
import os

# Link to the backend folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import answer_query

# Page Config [cite: 339, 340]
st.set_page_config(page_title="VTU Campus Assistant", page_icon="🎓")
st.title("Interactive Campus Info Agent")
st.markdown("Ask me about college rules, faculty, or event locations!")

# Sidebar for categories [cite: 340, 341]
with st.sidebar:
    st.header("Quick Access")
    if st.button("Exam Cell Location"):
        st.info("The Placement/Exam Cell is located in the Admin Block, Ground Floor.")
    if st.button("Hostel Rules"):
        st.warning("In-time for hostels is 9:00 PM.")

# Chat Interface [cite: 339]
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How do I join the drama club?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Calling the backend [cite: 933]
        response = answer_query(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})