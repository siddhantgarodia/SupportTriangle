"""
Supervisor agent: classifies incoming tickets into billing/technical/refund/other.
It has NO access to the knowledge base — its only job is routing.
Uses Groq structured output so we get a validated Pydantic model back.
"""
from pathlib import Path
import logging
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from schemas.ticket import TicketClassification

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "classify.txt"


def _get_llm():
    return ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        groq_api_key=GROQ_API_KEY,
    )


def classify_ticket(subject: str, message: str) -> TicketClassification:
    """
    Classify a ticket. Returns a TicketClassification.
    Retries once if structured output validation fails.
    Falls back to category='other' if both attempts fail.
    """
    prompt_template = _PROMPT_FILE.read_text(encoding="utf-8")
    prompt = prompt_template.format(subject=subject, message=message)

    llm = _get_llm().with_structured_output(TicketClassification)

    for attempt in range(2):
        try:
            result = llm.invoke(prompt)
            return result
        except Exception as e:
            if attempt == 0:
                logger.warning(f"Classification retry after error: {e}")
                continue
            logger.error(f"Classification failed after 2 attempts: {e}", exc_info=True)
            return TicketClassification(
                category="other",
                confidence=0.0,
                reasoning="Classification failed — defaulting to 'other' for human review.",
                suggested_priority="medium",
            )
