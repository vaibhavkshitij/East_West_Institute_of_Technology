import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Set API Key directly if environment variable is not used (not recommended for GitHub)
os.environ["GOOGLE_API_KEY"] = "gen-lang-client-0559556591"

def ingest_docs(pdf_path):
    """Processes a PDF handbook and saves a local FAISS index."""
    loader = PyPDFLoader(pdf_path) # Uses PyPDF2 under the hood [cite: 274, 285]
    data = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(data)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("faiss_campus_index")
    return vectorstore

def get_campus_qa_chain():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Check if index exists; if not, you must run ingest_docs first
    if not os.path.exists("faiss_campus_index"):
        raise FileNotFoundError("FAISS index not found. Please run document ingestion first.")
        
    vectorstore = FAISS.load_local("faiss_campus_index", embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3) [cite: 376]
    
    system_prompt = (
        "You are the East West Institute of Technology assistant. "
        "Use the retrieved campus info to answer accurately. "
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

def answer_query(query):
    rag_chain = get_campus_qa_chain()
    response = rag_chain.invoke({"input": query})
    return response["answer"]