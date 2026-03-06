import os
import sys

# Add the project root to path so 'backend' package is found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import ingest_docs

PDF_PATH = "data/handbook.pdf"

if not os.path.exists(PDF_PATH):
    print("ERROR: Place your college handbook PDF at " + PDF_PATH)
else:
    print("Starting Document Ingestion... This may take a minute.")
    try:
        ingest_docs(PDF_PATH)
        print("SUCCESS: 'faiss_campus_index' folder created!")
        print("Now you can run: streamlit run frontend/app.py")
    except Exception as e:
        print("Ingestion failed: " + str(e))