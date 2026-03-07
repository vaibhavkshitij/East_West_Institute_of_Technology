import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

FAISS_INDEX_PATH = "faiss_index"
EMBED_MODEL = "all-MiniLM-L6-v2"  # runs locally, no API key needed


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def ingest_docs(pdf_path: str):
    """Load a PDF, chunk it, embed it, and save a FAISS index locally."""
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    return len(chunks)


def index_exists():
    return os.path.exists(FAISS_INDEX_PATH)


def reset_chain_cache():
    global _chain_cache
    _chain_cache = None


_chain_cache = None


def _build_chain():
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # Groq is free - get key at https://console.groq.com
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful campus assistant for East West Institute of Technology. "
         "Answer questions using only the context provided. "
         "If the answer is not in the context, say you don't have that information. "
         "Be concise and friendly.\n\nContext:\n{context}"),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def answer_query(query: str) -> str:
    global _chain_cache
    if _chain_cache is None:
        _chain_cache = _build_chain()
    return _chain_cache.invoke(query)
