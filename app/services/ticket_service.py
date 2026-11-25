from sqlalchemy.orm import Session

from app.database.models import Customer, Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(
    db: Session,
    ticket_data: TicketCreate,
    *,
    owner_customer_id: int | None = None,
    normalized_subject: str | None = None,
    normalized_description: str | None = None,
    detected_language: str | None = None,
):
    if owner_customer_id is not None:
        customer = db.query(Customer).filter(Customer.id == owner_customer_id).first()
        if customer is None:
            raise ValueError("Customer profile is not available for this account.")
    else:
        if not ticket_data.customer_name or not ticket_data.customer_email:
            raise ValueError("Customer name and email are required when staff create a ticket.")
        email = str(ticket_data.customer_email).lower()
        customer = db.query(Customer).filter(Customer.email == email).first()
        if customer is None:
            customer = Customer(name=ticket_data.customer_name, email=email)
            db.add(customer)
            db.flush()

    ticket = Ticket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        normalized_subject=normalized_subject or ticket_data.subject,
        normalized_description=normalized_description or ticket_data.description,
        preferred_language=detected_language or ticket_data.preferred_language,
        customer_id=customer.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_all_tickets(db: Session):
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update_ticket(db: Session, ticket_id: int, update_data: TicketUpdate):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket
