
from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Numeric,
    Enum,
    Index,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from pgvector.sqlalchemy import Vector

from app.database.connection import Base


# ============================================================
# CUSTOM VECTOR TYPE
# PostgreSQL: pgvector
# SQLite: JSON (for local testing)
# ============================================================

class VectorOrJSON(TypeDecorator):

    impl = JSON
    cache_ok = True

    def __init__(self, dimensions=384):
        self.dimensions = dimensions
        super().__init__()

    def load_dialect_impl(self, dialect):

        if dialect.name == "postgresql":
            return dialect.type_descriptor(
                Vector(self.dimensions)
            )

        return dialect.type_descriptor(JSON())


# ============================================================
# ENUMS
# ============================================================

class TicketCategory(str, enum.Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    SUBSCRIPTION = "subscription"
    GENERAL = "general"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_HUMAN = "waiting_for_human"
    RESOLVED = "resolved"
    CLOSED = "closed"

# ============================================================
# CUSTOMER MODEL
# ============================================================

class Customer(Base):

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    tickets = relationship(
        "Ticket",
        back_populates="customer"
    )

    messages = relationship(
        "TicketMessage",
        back_populates="customer"
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="customer"
    )

    payments = relationship(
        "Payment",
        back_populates="customer"
    )


# ============================================================
# TICKET MODEL
# ============================================================

class Ticket(Base):

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    subject = Column(String(200), nullable=False)

    description = Column(Text, nullable=False)

    category = Column(
        Enum(
            TicketCategory.BILLING,
            TicketCategory.TECHNICAL,
            TicketCategory.ACCOUNT,
            TicketCategory.SUBSCRIPTION,
            TicketCategory.GENERAL,
            name="ticket_category",
            native_enum=False
        ),
        default=TicketCategory.GENERAL,
        nullable=False
    )

    priority = Column(
        Enum(
            TicketPriority.LOW,
            TicketPriority.MEDIUM,
            TicketPriority.HIGH,
            TicketPriority.CRITICAL,
            name="ticket_priority",
            native_enum=False
        ),
        default=TicketPriority.MEDIUM,
        nullable=False
    )

    status = Column(
        Enum(
            TicketStatus.OPEN,
            TicketStatus.IN_PROGRESS,
            TicketStatus.WAITING_FOR_HUMAN,
            TicketStatus.RESOLVED,
            TicketStatus.CLOSED,
            name="ticket_status",
            native_enum=False
        ),
        default=TicketStatus.OPEN,
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="tickets"
    )

    messages = relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )


# ============================================================
# TICKET MESSAGE MODEL
# ============================================================

class TicketMessage(Base):

    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    sender_type = Column(
        String(20),
        nullable=False
    )

    message = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    ticket = relationship(
        "Ticket",
        back_populates="messages"
    )

    customer = relationship(
        "Customer",
        back_populates="messages"
    )


# ============================================================
# SUBSCRIPTION MODEL
# ============================================================

class Subscription(Base):

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    plan_name = Column(String(100), nullable=False)

    status = Column(String(30), nullable=False)

    start_date = Column(DateTime, nullable=True)

    renewal_date = Column(DateTime, nullable=True)

    monthly_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    currency = Column(
        String(10),
        default="INR"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="subscriptions"
    )


# ============================================================
# PAYMENT MODEL
# ============================================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    currency = Column(
        String(10),
        default="INR"
    )

    status = Column(
        String(30),
        nullable=False
    )

    payment_method = Column(
        String(50),
        nullable=True
    )

    payment_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="payments"
    )


# ============================================================
# DOCUMENT MODEL
# Stores uploaded document metadata
# ============================================================

class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(
        String(255),
        nullable=False
    )

    file_type = Column(
        String(20),
        nullable=False
    )

    file_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    chunk_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )


# ============================================================
# DOCUMENT CHUNK MODEL
# Stores text chunks and their embeddings
# ============================================================

class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    embedding = Column(
        VectorOrJSON(384),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk"
        ),
    )


# ============================================================
# DATABASE INDEXES
# ============================================================

Index(
    "ix_ticket_messages_ticket_created",
    TicketMessage.ticket_id,
    TicketMessage.created_at
)

Index(
    "ix_payments_customer_date",
    Payment.customer_id,
    Payment.payment_date
)
# ============================================================
# HUMAN APPROVAL MODEL
# ============================================================

class ApprovalRequest(Base):

    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    action_type = Column(
        String(50),
        nullable=False
    )

    requested_action = Column(
        Text,
        nullable=False
    )

    reason = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True
    )

    reviewer_name = Column(
        String(100),
        nullable=True
    )

    review_note = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )


Index(
    "ix_approval_ticket_status",
    ApprovalRequest.ticket_id,
    ApprovalRequest.status
)