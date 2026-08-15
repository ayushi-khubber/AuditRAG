from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_policy_documents(
    policy_docs: list[dict], chunk_size: int = 400, chunk_overlap: int = 50
) -> list[Document]:
    """Split each policy document into overlapping chunks and tag each chunk
    with its source filename so findings can be traced back to a policy."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )

    chunks: list[Document] = []
    for doc in policy_docs:
        for piece in splitter.split_text(doc["text"]):
            piece = piece.strip()
            if piece:
                chunks.append(Document(page_content=piece, metadata={"source": doc["source"]}))
    return chunks
