import time

from src.config import (
    CONTROLS_PATH,
    POLICIES_DIR,
    COVERAGE_THRESHOLD,
    PARTIAL_THRESHOLD,
    EMBEDDING_MODEL,
)
from src.data_loader import load_controls, load_policy_documents
from src.chunking import chunk_policy_documents
from src.semantic_scorer import SemanticScorer
from src.retriever import build_vectorstore, retrieve_context
from src.llm_analysis import generate_gap_narrative


def _status_for_score(score: float) -> str:
    if score >= COVERAGE_THRESHOLD:
        return "Covered"
    if score >= PARTIAL_THRESHOLD:
        return "Partial"
    return "Gap"


def run_pipeline(generate_narratives: bool = True, verbose: bool = True) -> list[dict]:
    """
    End-to-end pipeline:
      1. Load NIST CSF 2.0 controls and organizational policy documents.
      2. Chunk the policy documents.
      3. Score every control against every policy chunk with Sentence-Transformers
         cosine similarity to find the best-matching evidence and a confidence score.
      4. Use a FAISS retriever to pull the top matching chunks as RAG context.
      5. Ask Llama 3.3 70B (via Groq) to write a short gap-analysis narrative
         grounded in that retrieved context.
    Returns a list of per-control finding dicts.
    """
    t0 = time.time()

    controls = load_controls(CONTROLS_PATH)
    policy_docs = load_policy_documents(POLICIES_DIR)
    chunks = chunk_policy_documents(policy_docs)

    if verbose:
        print(f"Loaded {len(controls)} controls and {len(policy_docs)} policy docs "
              f"({len(chunks)} chunks) using embedding model '{EMBEDDING_MODEL}'.")

    scorer = SemanticScorer(EMBEDDING_MODEL)
    vectorstore = build_vectorstore(chunks)

    findings = []
    for i, control in enumerate(controls, start=1):
        scored_chunks = scorer.best_match(control["description"], chunks)
        best_chunk, best_score = scored_chunks[0] if scored_chunks else (None, 0.0)
        status = _status_for_score(best_score)

        narrative = ""
        if generate_narratives:
            retrieved = retrieve_context(vectorstore, control["description"], k=3)
            narrative = generate_gap_narrative(control, retrieved)

        findings.append(
            {
                "id": control["id"],
                "function": control["function"],
                "category": control["category"],
                "description": control["description"],
                "status": status,
                "confidence": round(float(best_score), 3),
                "best_match_source": best_chunk.metadata.get("source") if best_chunk else None,
                "best_match_excerpt": best_chunk.page_content if best_chunk else None,
                "narrative": narrative,
            }
        )

        if verbose:
            print(f"  [{i}/{len(controls)}] {control['id']} -> {status} "
                  f"(confidence={best_score:.3f})")

    if verbose:
        elapsed = time.time() - t0
        print(f"Pipeline finished in {elapsed:.1f}s.")

    return findings
