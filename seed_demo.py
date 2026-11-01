
from datetime import date, datetime, timezone
from decimal import Decimal

from app.database.connection import Base, engine, SessionLocal
from app.database.models import (
    Customer,
    Ticket,
    TicketMessage,
    Subscription,
    Payment,
    TicketCategory,
    TicketPriority,
    TicketStatus
)

# Ensure all tables exist
import app.database.models


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        demo_customers = [
            {
                "name": "Rahul Sharma",
                "email": "rahul@example.com",
                "plan": "Pro",
                "price": Decimal("999.00"),
                "transaction": "TXN1001",
                "amount": Decimal("999.00"),
                "payment_status": "success"
            },
            {
                "name": "Priya Reddy",
                "email": "priya@example.com",
                "plan": "Basic",
                "price": Decimal("499.00"),
                "transaction": "TXN1002",
                "amount": Decimal("499.00"),
                "payment_status": "success"
            },
            {
                "name": "Arjun Kumar",
                "email": "arjun@example.com",
                "plan": "Enterprise",
                "price": Decimal("4999.00"),
                "transaction": "TXN1003",
                "amount": Decimal("4999.00"),
                "payment_status": "failed"
            }
        ]

        customers = {}

        for item in demo_customers:
            customer = db.query(Customer).filter_by(
                email=item["email"]
            ).first()

            if not customer:
                customer = Customer(
                    name=item["name"],
                    email=item["email"]
                )
                db.add(customer)
                db.flush()

            customers[item["email"]] = customer

            subscription = db.query(Subscription).filter_by(
                customer_id=customer.id
            ).first()

            if not subscription:
                db.add(
                    Subscription(
                        customer_id=customer.id,
                        plan_name=item["plan"],
                        status="active",
                        start_date=date(2026, 1, 1),
                        renewal_date=date(2026, 12, 1),
                        monthly_price=item["price"],
                        currency="INR"
                    )
                )

            payment = db.query(Payment).filter_by(
                transaction_id=item["transaction"]
            ).first()

            if not payment:
                db.add(
                    Payment(
                        customer_id=customer.id,
                        transaction_id=item["transaction"],
                        amount=item["amount"],
                        currency="INR",
                        status=item["payment_status"],
                        payment_method="UPI",
                        payment_date=datetime.now(timezone.utc)
                    )
                )

        db.commit()

        # Create example tickets
        sample_tickets = [
            {
                "email": "rahul@example.com",
                "subject": "Duplicate payment",
                "description": "I was charged twice for my Pro subscription.",
                "category": TicketCategory.BILLING,
                "priority": TicketPriority.HIGH
            },
            {
                "email": "priya@example.com",
                "subject": "Cannot log in",
                "description": "I cannot access my account after resetting my password.",
                "category": TicketCategory.ACCOUNT,
                "priority": TicketPriority.MEDIUM
            },
            {
                "email": "arjun@example.com",
                "subject": "Payment failed",
                "description": "My subscription payment failed but money appears to have been deducted.",
                "category": TicketCategory.BILLING,
                "priority": TicketPriority.HIGH
            }
        ]

        for item in sample_tickets:
            customer = customers[item["email"]]

            ticket = db.query(Ticket).filter_by(
                customer_id=customer.id,
                subject=item["subject"]
            ).first()

            if not ticket:
                ticket = Ticket(
                    customer_id=customer.id,
                    subject=item["subject"],
                    description=item["description"],
                    category=item["category"],
                    priority=item["priority"],
                    status=TicketStatus.OPEN
                )

                db.add(ticket)
                db.flush()

                db.add(
                    TicketMessage(
                        ticket_id=ticket.id,
                        customer_id=customer.id,
                        sender_type="customer",
                        message=item["description"]
                    )
                )

        db.commit()

        print("Demo data seeded successfully!")
        print("Customers:", db.query(Customer).count())
        print("Tickets:", db.query(Ticket).count())
        print("Subscriptions:", db.query(Subscription).count())
        print("Payments:", db.query(Payment).count())
        print("Messages:", db.query(TicketMessage).count())

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
