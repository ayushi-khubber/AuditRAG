from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document


class SemanticScorer:
    """Wraps a Sentence-Transformers model and scores how semantically close a
    NIST control description is to each policy chunk using cosine similarity.
    This is what produces the confidence score behind each finding."""

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def best_match(
        self, control_text: str, policy_chunks: list[Document]
    ) -> list[tuple[Document, float]]:
        """Return (chunk, similarity) pairs sorted by similarity, descending."""
        if not policy_chunks:
            return []

        control_embedding = self.model.encode([control_text])
        chunk_texts = [c.page_content for c in policy_chunks]
        chunk_embeddings = self.model.encode(chunk_texts)

        similarities = cosine_similarity(control_embedding, chunk_embeddings)[0]
        scored = list(zip(policy_chunks, similarities.tolist()))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored
