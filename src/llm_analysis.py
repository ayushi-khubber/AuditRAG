from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = (
    "You are a compliance analyst assistant. Given a NIST CSF 2.0 control requirement and "
    "excerpts retrieved from an organization's security policies, write a concise 2-3 "
    "sentence gap analysis. State whether the policy fully addresses the control, partially "
    "addresses it, or does not address it, and name the specific requirement that is missing "
    "or weak. Do not restate the whole control text back verbatim."
)


def generate_gap_narrative(control: dict, retrieved_chunks: list[Document]) -> str:
    """Calls Llama 3.3 70B (hosted on Groq) with the control + retrieved policy
    context to produce a human-readable gap analysis. Falls back to a plain
    message if no GROQ_API_KEY is configured, so the rest of the app still runs."""
    if not GROQ_API_KEY:
        return (
            "[Narrative generation skipped — no GROQ_API_KEY set in .env. "
            "The similarity score and matched excerpt below are still valid.]"
        )

    # Imported lazily so the whole app doesn't hard-fail on import if the
    # optional langchain-groq package isn't installed for some reason.
    from langchain_groq import ChatGroq

    context = (
        "\n\n".join(
            f"[Source: {c.metadata.get('source', 'unknown')}]\n{c.page_content}"
            for c in retrieved_chunks
        )
        or "No relevant policy text was retrieved for this control."
    )

    llm = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.2)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Control {control['id']} ({control['function']} / {control['category']}): "
                f"{control['description']}\n\nRetrieved policy excerpts:\n{context}"
            )
        ),
    ]

    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as exc:  # noqa: BLE001 - surface the error, don't crash the pipeline
        return f"[LLM call failed: {exc}]"
