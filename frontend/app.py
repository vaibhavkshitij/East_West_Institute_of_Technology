import streamlit as st
import tempfile
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import answer_query, ingest_docs, reset_chain_cache, index_exists

st.set_page_config(page_title="EWIT Campus Assistant", page_icon="🎓", layout="centered")

st.title("🎓 EWIT Campus Assistant")
st.caption("Powered by Groq (free) + LLaMA3 · Ask anything about campus!")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Handbook")
    uploaded_file = st.file_uploader("Upload campus PDF", type=["pdf"])

    if uploaded_file:
        if st.button("📥 Ingest Document", use_container_width=True):
            with st.spinner("Embedding document... (first time may take ~30s)"):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    count = ingest_docs(tmp_path)
                    os.unlink(tmp_path)
                    reset_chain_cache()
                    st.success(f"✅ Ingested {count} chunks!")
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")

    st.divider()

    if index_exists():
        st.success("✅ Knowledge base loaded")
    else:
        st.warning("⚠️ No knowledge base yet.\nUpload a PDF above.")

    st.divider()
    st.header("⚡ Quick Questions")
    quick = [
        "Where is the exam cell?",
        "What are hostel timings?",
        "How do I join a club?",
        "Who is the principal?",
    ]
    for q in quick:
        if st.button(q, use_container_width=True):
            st.session_state.pending_question = q

# ── Chat ──────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle quick-question button clicks
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
else:
    prompt = st.chat_input("Ask about campus rules, events, faculty...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if not index_exists():
                    response = "⚠️ Please upload and ingest a campus PDF first using the sidebar."
                else:
                    response = answer_query(prompt)
            except Exception as e:
                response = f"❌ Error: {e}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
