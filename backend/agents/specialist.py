"""
Unified parametrized specialist agent. Loads persona prompt from the DB
so edits take effect immediately without restart.
"""
from langchain_groq import ChatGroq
from ..config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, RETRIEVAL_TOP_K
from ..schemas.ticket import Ticket
from ..schemas.response import DraftResponse, DraftWithCitations, KBCitation
from ..rag.retriever import retrieve_kb_context
from ..db import PersonaModel, get_session

_FALLBACK_DRAFT = DraftResponse(
    response_text=(
        "Thank you for reaching out. This ticket has been flagged for manual review "
        "by a specialist who will respond within one business day."
    ),
    cited_chunk_ids=[],
    confidence=0.0,
    suggested_action="escalate",
    tone_notes="Auto-fallback — LLM call failed.",
)


def _get_llm():
    return ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        groq_api_key=GROQ_API_KEY,
    )


def _load_persona_prompt(category: str) -> str:
    session = get_session()
    try:
        persona = session.query(PersonaModel).filter_by(category=category).first()
        if not persona:
            raise RuntimeError(f"No persona found for '{category}' — did seed run?")
        return persona.prompt_template
    finally:
        session.close()


def _format_few_shot_block(examples: list[dict]) -> str:
    if not examples:
        return "No prior approved examples available yet."
    blocks = []
    for i, ex in enumerate(examples, 1):
        blocks.append(
            f"Example {i} (similarity {ex['similarity']:.2f}):\n"
            f"Customer ticket: {ex['ticket_message']}\n"
            f"Approved response: {ex['final_response']}\n"
        )
    return "\n---\n".join(blocks)


def _format_kb_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant knowledge base chunks found."
    return "\n\n".join(
        f"[{c['chunk_id']}] (from {c['source_file']}):\n{c['content']}"
        for c in chunks
    )


def draft_specialist_response(
    category: str,
    ticket: Ticket,
    few_shot_examples: list[dict],
) -> DraftWithCitations:
    if category not in ("billing", "technical", "refund"):
        raise ValueError(f"Invalid category for specialist: {category}")

    chunks = retrieve_kb_context(query=ticket.message, namespace=category, top_k=RETRIEVAL_TOP_K)
    if not chunks:
        chunks = retrieve_kb_context(query=ticket.subject, namespace=category, top_k=RETRIEVAL_TOP_K)

    persona_template = _load_persona_prompt(category)
    prompt = persona_template.format(
        kb_context=_format_kb_context(chunks),
        few_shot_block=_format_few_shot_block(few_shot_examples),
        customer_name=ticket.customer_name,
        subject=ticket.subject,
        message=ticket.message,
    )

    llm = _get_llm().with_structured_output(DraftResponse)

    for attempt in range(2):
        try:
            draft = llm.invoke(prompt)
            break
        except Exception as e:
            if attempt == 0:
                print(f"[Specialist:{category}] Retry after error: {e}")
                continue
            print(f"[Specialist:{category}] Both attempts failed: {e}")
            draft = _FALLBACK_DRAFT

    citations = [
        KBCitation(
            chunk_id=c["chunk_id"],
            content=c["content"],
            source_file=c["source_file"],
            namespace=category,
        )
        for c in chunks
    ]
    return DraftWithCitations(draft=draft, citations=citations)
