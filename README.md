🏫 Interactive Campus Info AI Agent - EWIT

Track A: Essential 

📖 Project Overview
This AI-powered campus assistant is designed for students and visitors of the East West Institute of Technology. It ingests college handbooks and department data to provide instant answers regarding academic regulations, campus facilities, and college procedures.
+1

🎥 Project Prototype

Demo Video Link: https://drive.google.com/file/d/15ls1YyZNQYTZQp1SZY-9Qw1x8F67sSil/view?usp=sharing




🗓️ Project Roadmap (Bi-Weekly Plan) 


Past 2 Weeks (Weeks 1-2): Foundation 
+1


Environment Setup: Configured Python environment with LangChain, Streamlit, and FAISS.


Data Ingestion: Implemented PyPDFLoader to process the EWIT Student Handbook.


Core Logic: Built a RAG (Retrieval-Augmented Generation) pipeline using Groq (LLaMA 3.1 8B Instant) and HuggingFace Embeddings (all-MiniLM-L6-v2) running locally.
+1


Initial Deployment: Successfully deployed the base version on Streamlit Cloud.


Upcoming 2 Weeks (Weeks 3-4): Core Architecture 
+1


Day 1-3: Integrate BeautifulSoup for real-time scraping of the official college website.


Day 4-7: Implement an Event Calendar tool to track upcoming internal exams and fests.


Day 8-10: Build a Contact Directory search for faculty and department heads.


Day 11-14: Add basic campus map integration for building locations.

💻 Tech Stack 


Frontend: Streamlit 


Backend: Python + LangChain 


LLM: Groq - LLaMA 3.1 8B Instant (Free, no billing required) 


Embeddings: HuggingFace all-MiniLM-L6-v2 (runs locally, no API key needed) 


Vector Database: FAISS 


APIs: Groq API (free tier)
