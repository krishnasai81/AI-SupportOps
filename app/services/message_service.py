
from sqlalchemy.orm import Session

from app.database.models import (
    Ticket,
    TicketMessage,
    Customer
)


def add_message(
    db: Session,
    ticket_id: int,
    sender_type: str,
    message: str
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        return None

    if sender_type not in {"customer", "support", "agent"}:
        raise ValueError("Invalid sender type")

    new_message = TicketMessage(
        ticket_id=ticket.id,
        customer_id=ticket.customer_id,
        sender_type=sender_type,
        message=message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


def get_ticket_messages(db: Session, ticket_id: int):
    return (
        db.query(TicketMessage)
        .filter(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at.asc())
        .all()
    )


def get_customer_messages(db: Session, customer_id: int):
    return (
        db.query(TicketMessage)
        .filter(TicketMessage.customer_id == customer_id)
        .order_by(TicketMessage.created_at.desc())
        .all()
    )
