from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.config import EMBEDDING_MODEL


def build_vectorstore(chunks: list[Document]) -> FAISS:
    """Embed every policy chunk with Sentence-Transformers and index it in
    FAISS so the LLM step can retrieve relevant context per control."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.from_documents(chunks, embeddings)


def retrieve_context(vectorstore: FAISS, query: str, k: int = 3) -> list[Document]:
    return vectorstore.similarity_search(query, k=k)
