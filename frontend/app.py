import streamlit as st
import tempfile
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  
from backend.main import answer_query, ingest_docs, reset_chain_cache

# Page Config
st.set_page_config(page_title="VTU Campus Assistant", page_icon="🎓")
st.title("🎓 Interactive Campus Info Agent")
st.markdown("Ask me about college rules, faculty, or event locations!")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Handbook")
    uploaded_file = st.file_uploader("Upload campus PDF", type=["pdf"])

    if uploaded_file:
        if st.button("📥 Ingest Document"):
            with st.spinner("Processing PDF..."):
                try:
                    # Save upload to a temp file and ingest
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    ingest_docs(tmp_path)
                    os.unlink(tmp_path)          # clean up temp file
                    reset_chain_cache()          # force chain rebuild with new index
                    st.success("✅ Document ingested! You can now ask questions.")
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")

    st.divider()
    st.header("⚡ Quick Access")
    if st.button("Exam Cell Location"):
        st.info("The Exam Cell is located in the Admin Block, Ground Floor.")
    if st.button("Hostel Rules"):
        st.warning("In-time for hostels is 9:00 PM.")

# ── Chat Interface ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("How do I join the drama club?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = answer_query(prompt)
            except FileNotFoundError:
                response = (
                    "⚠️ No document has been ingested yet. "
                    "Please upload a campus PDF using the sidebar first."
                )
            except Exception as e:
                response = f"❌ Something went wrong: {e}"

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
