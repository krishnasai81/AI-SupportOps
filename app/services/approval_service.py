
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import (
    ApprovalRequest,
    Ticket,
    TicketMessage,
)


def create_approval_request(
    db: Session,
    ticket: Ticket,
    action_type: str,
    reason: str,
) -> ApprovalRequest:

    existing = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.ticket_id == ticket.id,
            ApprovalRequest.status == "pending",
        )
        .first()
    )

    if existing:
        return existing

    descriptions = {
        "refund": (
            "Review the customer's refund request. "
            "No payment action will be executed automatically."
        ),
        "account_modification": (
            "Review the requested account modification. "
            "No account changes will be made automatically."
        ),
        "subscription_modification": (
            "Review the requested subscription modification. "
            "No subscription changes will be made automatically."
        ),
        "security_concern": (
            "Review the reported security concern."
        ),
        "manual_review": (
            "Review this ticket due to its priority "
            "or classification uncertainty."
        ),
    }

    approval = ApprovalRequest(
        ticket_id=ticket.id,
        customer_id=ticket.customer_id,
        action_type=action_type,
        requested_action=descriptions.get(
            action_type,
            descriptions["manual_review"],
        ),
        reason=reason,
        status="pending",
    )

    db.add(approval)
    db.flush()

    return approval


def get_pending_approvals(db: Session):

    return (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.status == "pending")
        .order_by(ApprovalRequest.created_at.asc())
        .all()
    )


def get_approval_by_id(
    db: Session,
    approval_id: int,
):

    return (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.id == approval_id)
        .first()
    )


def decide_approval(
    db: Session,
    approval_id: int,
    decision: str,
    reviewer_name: str,
    review_note: str | None,
):

    if decision not in ("approve", "reject"):
        raise ValueError("Decision must be approve or reject.")

    approval = get_approval_by_id(db, approval_id)

    if not approval:
        return None

    if approval.status != "pending":
        raise ValueError(
            "This approval request has already been reviewed."
        )

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == approval.ticket_id)
        .with_for_update()
        .first()
    )

    if not ticket:
        raise ValueError(
            "The associated ticket no longer exists."
        )

    approval.status = (
        "approved" if decision == "approve" else "rejected"
    )

    approval.reviewer_name = reviewer_name.strip()
    approval.review_note = review_note
    approval.reviewed_at = datetime.utcnow()

    ticket.status = "in_progress"

    if decision == "approve":
        message = (
            f"Human review approved by {reviewer_name}. "
            "The requested action is authorized for a separately "
            "controlled manual process. No external action was "
            "executed automatically."
        )
    else:
        message = (
            f"Human review rejected by {reviewer_name}. "
            "The requested action was not authorized."
        )

    if review_note:
        message += f" Reviewer note: {review_note}"

    db.add(
        TicketMessage(
            ticket_id=ticket.id,
            customer_id=ticket.customer_id,
            sender_type="support",
            message=message,
        )
    )

    db.commit()
    db.refresh(approval)

    return approval
