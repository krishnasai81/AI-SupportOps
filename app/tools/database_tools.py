
from sqlalchemy.orm import Session

from app.database.models import (
    Customer,
    Ticket,
    Payment,
    Subscription
)


def find_customer_by_email(db: Session, email: str):
    return db.query(Customer).filter(
        Customer.email == email.lower().strip()
    ).first()


def get_customer_tickets(db: Session, customer_id: int):
    return (
        db.query(Ticket)
        .filter(Ticket.customer_id == customer_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )


def get_customer_payments(db: Session, customer_id: int):
    return (
        db.query(Payment)
        .filter(Payment.customer_id == customer_id)
        .order_by(Payment.payment_date.desc())
        .all()
    )


def get_payment_by_transaction(db: Session, transaction_id: str):
    return db.query(Payment).filter(
        Payment.transaction_id == transaction_id
    ).first()


def get_customer_subscriptions(db: Session, customer_id: int):
    return db.query(Subscription).filter(
        Subscription.customer_id == customer_id
    ).all()


def get_customer_by_id(db: Session, customer_id: int):
    return db.query(Customer).filter(
        Customer.id == customer_id
    ).first()
