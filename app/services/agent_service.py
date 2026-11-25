from sqlalchemy.orm import Session

from app.database.models import Ticket, TicketMessage, ApprovalRequest
from app.workflow.graph import build_support_graph
from app.agents.escalation_agent import detect_sensitive_action
from app.services.approval_service import create_approval_request
from app.services.translation_service import localize_response


async def process_ticket(db: Session, ticket_id: int) -> dict | None:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        return None

    source_subject = ticket.normalized_subject or ticket.subject
    source_description = ticket.normalized_description or ticket.description
    visual_messages = (
        db.query(TicketMessage)
        .filter(
            TicketMessage.ticket_id == ticket.id,
            TicketMessage.message.like("Visual evidence (Mirage):%"),
        )
        .order_by(TicketMessage.created_at.asc())
        .all()
    )
    visual_evidence = [message.message for message in visual_messages]
    agent_description = source_description
    if visual_evidence:
        agent_description += "\n\nVisual evidence from customer-provided image(s):\n" + "\n".join(visual_evidence)

    sensitive_action = detect_sensitive_action(f"{source_subject} {source_description}")
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

    initial_state = {
        "ticket_id": ticket.id,
        "customer_id": ticket.customer_id,
        "customer_email": ticket.customer.email,
        "subject": source_subject,
        "description": agent_description,
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
        "existing_approval_status": existing_approval.status if existing_approval else "",
        "existing_approval_action": existing_approval.action_type if existing_approval else "",
        "existing_approval_id": existing_approval.id if existing_approval else None,
        "current_agent": "",
        "agent_trace": [],
        "error": "",
    }

    workflow = build_support_graph(db)
    result = await workflow.ainvoke(initial_state)

    try:
        ticket.category = result["category"]
        ticket.priority = result["priority"]
        ticket.status = "waiting_for_human" if result["needs_human_review"] else "in_progress"

        approval_id = existing_approval.id if existing_approval else None
        if result["needs_human_review"]:
            approval = create_approval_request(
                db=db,
                ticket=ticket,
                action_type=result["approval_action"] or "manual_review",
                reason=result["escalation_reason"],
            )
            approval_id = approval.id

        customer_response = await localize_response(
            result["final_response"],
            ticket.preferred_language or "en",
        )
        existing_message = (
            db.query(TicketMessage)
            .filter(
                TicketMessage.ticket_id == ticket.id,
                TicketMessage.sender_type == "agent",
                TicketMessage.message == customer_response,
            )
            .first()
        )
        if not existing_message:
            db.add(TicketMessage(
                ticket_id=ticket.id,
                customer_id=ticket.customer_id,
                sender_type="agent",
                message=customer_response,
            ))
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise

    return {
        "ticket_id": ticket.id,
        "category": result["category"],
        "priority": result["priority"],
        "classification_confidence": result["classification_confidence"],
        "supervisor_decision": result["supervisor_decision"],
        "knowledge_found": result["knowledge_found"],
        "troubleshooting_steps": result["troubleshooting_steps"],
        "response": customer_response,
        "needs_human_review": result["needs_human_review"],
        "approval_action": result["approval_action"],
        "approval_id": approval_id,
        "approval_status": existing_approval.status if existing_approval else ("pending" if result["needs_human_review"] else None),
        "escalation_reason": result["escalation_reason"],
        "status": ticket.status,
        "agent_trace": result["agent_trace"],
        "visual_evidence_count": len(visual_evidence),
        "language": ticket.preferred_language or "en",
    }
