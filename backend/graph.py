"""
LangGraph multi-agent pipeline:
  START → supervisor → fetch_few_shot → [router] → {billing|technical|refund|fallback} → END
"""
from typing import Optional, TypedDict
import logging
from langgraph.graph import StateGraph, END
from schemas.ticket import Ticket, TicketClassification
from schemas.response import DraftWithCitations
from agents.supervisor import classify_ticket
from agents.specialist import draft_specialist_response
from agents.fallback import fallback_draft
from few_shot import get_few_shot_examples
from config import CLASSIFICATION_MIN_CONFIDENCE

logger = logging.getLogger(__name__)


class TriageState(TypedDict):
    ticket: Ticket
    classification: Optional[TicketClassification]
    few_shot_examples: list[dict]
    draft_with_citations: Optional[DraftWithCitations]
    log: list[str]
    error: Optional[str]


def supervisor_node(state: TriageState) -> TriageState:
    state["log"].append("Supervisor: classifying...")
    try:
        state["classification"] = classify_ticket(
            subject=state["ticket"].subject,
            message=state["ticket"].message,
        )
        cls = state["classification"]
        state["log"].append(f"Classified as {cls.category} (conf: {cls.confidence:.2f})")
    except Exception as e:
        state["error"] = f"Supervisor failed: {e}"
        state["log"].append(state["error"])
    return state


def fetch_few_shot_node(state: TriageState) -> TriageState:
    cls = state.get("classification")
    if not cls or cls.category == "other":
        state["few_shot_examples"] = []
        return state
    state["few_shot_examples"] = get_few_shot_examples(
        ticket_message=state["ticket"].message,
        category=cls.category,
    )
    state["log"].append(f"Loaded {len(state['few_shot_examples'])} few-shot examples")
    return state


def specialist_node_factory(category: str):
    def node(state: TriageState) -> TriageState:
        state["log"].append(f"Specialist ({category}): drafting...")
        try:
            state["draft_with_citations"] = draft_specialist_response(
                category=category,
                ticket=state["ticket"],
                few_shot_examples=state["few_shot_examples"],
            )
            state["log"].append("Draft ready")
        except Exception as e:
            state["error"] = f"Specialist failed: {e}"
            state["log"].append(state["error"])
            state["draft_with_citations"] = fallback_draft()
        return state
    return node


def fallback_node(state: TriageState) -> TriageState:
    state["log"].append("Routing to fallback (human review)")
    state["draft_with_citations"] = fallback_draft()
    return state


def route_to_specialist(state: TriageState) -> str:
    cls = state.get("classification")
    if not cls or cls.confidence < CLASSIFICATION_MIN_CONFIDENCE:
        return "fallback"
    if cls.category in ("billing", "technical", "refund"):
        return cls.category
    return "fallback"


_graph = None


def _build_graph():
    g = StateGraph(TriageState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("fetch_few_shot", fetch_few_shot_node)
    g.add_node("billing", specialist_node_factory("billing"))
    g.add_node("technical", specialist_node_factory("technical"))
    g.add_node("refund", specialist_node_factory("refund"))
    g.add_node("fallback", fallback_node)

    g.set_entry_point("supervisor")
    g.add_edge("supervisor", "fetch_few_shot")
    g.add_conditional_edges(
        "fetch_few_shot",
        route_to_specialist,
        {"billing": "billing", "technical": "technical", "refund": "refund", "fallback": "fallback"},
    )
    for terminal in ("billing", "technical", "refund", "fallback"):
        g.add_edge(terminal, END)
    return g.compile()


def run_triage_pipeline(ticket: Ticket) -> tuple[Optional[TicketClassification], DraftWithCitations]:
    global _graph
    if _graph is None:
        _graph = _build_graph()

    initial_state: TriageState = {
        "ticket": ticket,
        "classification": None,
        "few_shot_examples": [],
        "draft_with_citations": None,
        "log": [],
        "error": None,
    }
    final_state = _graph.invoke(initial_state)
    logger.debug(f"Pipeline for {ticket.id}: {' -> '.join(final_state['log'])}")

    classification = final_state.get("classification")
    if final_state["draft_with_citations"] is None:
        from schemas.response import DraftResponse
        return classification, DraftWithCitations(
            draft=DraftResponse(
                response_text="Pipeline failed — please handle manually.",
                cited_chunk_ids=[],
                confidence=0.0,
                suggested_action="escalate",
            ),
            citations=[],
        )
    return classification, final_state["draft_with_citations"]
