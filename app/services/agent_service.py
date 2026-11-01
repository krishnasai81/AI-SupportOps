from sqlalchemy.orm import Session

from app.database.models import (
    Ticket,
    TicketMessage,
    ApprovalRequest,
)

from app.workflow.graph import build_support_graph
from app.agents.escalation_agent import detect_sensitive_action
from app.services.approval_service import create_approval_request


async def process_ticket(
    db: Session,
    ticket_id: int
) -> dict | None:

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        return None

    # Detect the sensitive action from the ticket.
    sensitive_action = detect_sensitive_action(
        f"{ticket.subject} {ticket.description}"
    )

    # Retrieve the latest approval for this ticket and action.
    existing_approval = None

    if sensitive_action:

        existing_approval = (
            db.query(ApprovalRequest)
            .filter(
                ApprovalRequest.ticket_id == ticket.id,
                ApprovalRequest.action_type == sensitive_action,
            )
            .order_by(ApprovalRequest.created_at.desc())
            .first()
        )

    # Prepare approval information for LangGraph.
    existing_approval_status = (
        existing_approval.status if existing_approval else ""
    )

    existing_approval_action = (
        existing_approval.action_type if existing_approval else ""
    )

    existing_approval_id = (
        existing_approval.id if existing_approval else None
    )

    initial_state = {

        "ticket_id": ticket.id,
        "customer_id": ticket.customer_id,
        "customer_email": ticket.customer.email,

        "subject": ticket.subject,
        "description": ticket.description,

        "category": "general",
        "priority": "medium",
        "classification_confidence": 0.0,

        "supervisor_decision": "",

        "knowledge_context": [],
        "knowledge_found": False,

        "troubleshooting_steps": [],

        "draft_response": "",
        "final_response": "",

        "needs_human_review": False,
        "escalation_reason": "",
        "approval_action": "",

        # Previous approval information
        "existing_approval_status": existing_approval_status,
        "existing_approval_action": existing_approval_action,
        "existing_approval_id": existing_approval_id,

        "current_agent": "",
        "agent_trace": [],
        "error": "",
    }

    workflow = build_support_graph(db)

    result = await workflow.ainvoke(initial_state)

    try:

        ticket.category = result["category"]
        ticket.priority = result["priority"]

        ticket.status = (
            "waiting_for_human"
            if result["needs_human_review"]
            else "in_progress"
        )

        approval_id = existing_approval_id

        # Create a new approval only when review is required.
        if result["needs_human_review"]:

            action_type = (
                result["approval_action"] or "manual_review"
            )

            approval = create_approval_request(
                db=db,
                ticket=ticket,
                action_type=action_type,
                reason=result["escalation_reason"],
            )

            approval_id = approval.id

        # Avoid duplicate agent messages.
        final_response = result["final_response"]

        existing_message = (
            db.query(TicketMessage)
            .filter(
                TicketMessage.ticket_id == ticket.id,
                TicketMessage.sender_type == "agent",
                TicketMessage.message == final_response,
            )
            .first()
        )

        if not existing_message:

            db.add(
                TicketMessage(
                    ticket_id=ticket.id,
                    customer_id=ticket.customer_id,
                    sender_type="agent",
                    message=final_response,
                )
            )

        db.commit()
        db.refresh(ticket)

    except Exception:

        db.rollback()
        raise

    return {
        "ticket_id": ticket.id,
        "category": result["category"],
        "priority": result["priority"],
        "classification_confidence": result[
            "classification_confidence"
        ],
        "supervisor_decision": result["supervisor_decision"],
        "knowledge_found": result["knowledge_found"],
        "troubleshooting_steps": result["troubleshooting_steps"],
        "response": result["final_response"],
        "needs_human_review": result["needs_human_review"],
        "approval_action": result["approval_action"],
        "approval_id": approval_id,
        "approval_status": existing_approval_status,
        "escalation_reason": result["escalation_reason"],
        "status": ticket.status,
        "agent_trace": result["agent_trace"],
    }