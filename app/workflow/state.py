from typing import TypedDict


class SupportState(TypedDict):

    ticket_id: int
    customer_id: int
    customer_email: str

    subject: str
    description: str

    category: str
    priority: str
    classification_confidence: float

    supervisor_decision: str

    knowledge_context: list[dict]
    knowledge_found: bool

    troubleshooting_steps: list[str]

    draft_response: str
    final_response: str

    needs_human_review: bool
    escalation_reason: str
    approval_action: str

    # Existing human approval information
    existing_approval_status: str
    existing_approval_action: str
    existing_approval_id: int | None

    current_agent: str
    agent_trace: list[str]
    error: str