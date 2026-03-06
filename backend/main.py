import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load API key from .env file (create a .env file with: GOOGLE_API_KEY=your_key_here)
load_dotenv()

FAISS_INDEX_PATH = "faiss_campus_index"


def ingest_docs(pdf_path: str):
    """Processes a PDF handbook and saves a local FAISS index."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at path: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(data)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"✅ Ingested {len(docs)} chunks. FAISS index saved to '{FAISS_INDEX_PATH}'.")
    return vectorstore


def _build_qa_chain():
    """Internal: builds and returns the RAG chain. Call once and cache."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            "FAISS index not found. Please upload and ingest a PDF first."
        )

    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever()

    # Use gemini-1.5-flash (gemini-pro is deprecated)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=0.3)

    system_prompt = (
        "You are the East West Institute of Technology assistant. "
        "Use the retrieved campus info to answer accurately. "
        "If the answer is not in the context, say you don't know. "
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    return (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


# Module-level cache — chain is built only once per session
_chain_cache = None


def get_cached_chain():
    global _chain_cache
    if _chain_cache is None:
        _chain_cache = _build_qa_chain()
    return _chain_cache


def reset_chain_cache():
    """Call this after ingesting a new document to force chain rebuild."""
    global _chain_cache
    _chain_cache = None


def answer_query(query: str) -> str:
    """Returns an answer string for the given query using the RAG chain."""
    rag_chain = get_cached_chain()
    return rag_chain.invoke(query)
