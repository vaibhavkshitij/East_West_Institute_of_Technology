import streamlit as st
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

# 1. Setup Streamlit Page Configuration [cite: 481, 590]
st.set_page_config(page_title="EWIT Campus Info Bot", layout="wide")
st.header("🏫 Interactive Campus Info AI Agent")

# 2. Document Processing Logic [cite: 537, 1388]
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# 3. Vector Store Creation (FAISS) [cite: 536, 626]
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# 4. Conversational AI Chain Setup [cite: 628]
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in
    provided context, just say, "The information is not available in the current campus documents," 
    don't provide the wrong answer.\n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

# 5. User Input Handling [cite: 596, 683]
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    st.write("Reply: ", response["output_text"])

# 6. Sidebar for Document Uploads [cite: 592, 1331]
with st.sidebar:
    st.title("Menu:")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    pdf_docs = st.file_uploader("Upload Campus Handbooks (PDFs)", accept_multiple_files=True)
    if st.button("Submit & Process"):
        with st.spinner("Processing documents..."):
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            st.success("Done! Your Campus Agent is ready.")

# 7. Main Chat Interface
user_question = st.text_input("Ask about college rules, placements, or facilities:")
if user_question:
    user_input(user_question)