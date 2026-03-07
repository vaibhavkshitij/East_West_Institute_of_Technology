import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.main import ingest_docs

PDF_PATH = "data/handbook.pdf"

if not os.path.exists(PDF_PATH):
    print(f"ERROR: Place your college handbook PDF at '{PDF_PATH}'")
else:
    print("Starting ingestion... (first run downloads embedding model ~90MB)")
    try:
        count = ingest_docs(PDF_PATH)
        print(f"SUCCESS: Ingested {count} chunks into 'faiss_index'")
        print("Now run: streamlit run frontend/app.py")
    except Exception as e:
        print(f"Ingestion failed: {e}")
