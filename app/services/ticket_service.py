from sqlalchemy.orm import Session

from app.database.models import (
    Customer,
    Ticket,
    TicketStatus
)

from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(db: Session, ticket_data: TicketCreate):

    customer = db.query(Customer).filter(
        Customer.email == ticket_data.customer_email
    ).first()

    if not customer:

        customer = Customer(
            name=ticket_data.customer_name,
            email=ticket_data.customer_email
        )

        db.add(customer)
        db.flush()

    ticket = Ticket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        customer_id=customer.id
    )

    db.add(ticket)

    db.commit()

    db.refresh(ticket)

    return ticket


def get_all_tickets(db: Session):

    return db.query(Ticket).order_by(
        Ticket.created_at.desc()
    ).all()


def get_ticket_by_id(db: Session, ticket_id: int):

    return db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()


def update_ticket(
    db: Session,
    ticket_id: int,
    update_data: TicketUpdate
):

    ticket = get_ticket_by_id(db, ticket_id)

    if not ticket:
        return None

    updates = update_data.model_dump(exclude_unset=True)

    for field, value in updates.items():

        setattr(ticket, field, value)

    db.commit()

    db.refresh(ticket)

    return ticket   