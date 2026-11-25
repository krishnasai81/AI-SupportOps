from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional

from app.database.models import TicketCategory, TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    # These fields are used only when a support/admin user creates a ticket
    # on behalf of an existing or new customer. Customer users cannot override
    # their identity with request-body values.
    customer_name: str | None = Field(default=None, min_length=2, max_length=100)
    customer_email: EmailStr | None = None
    subject: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10)
    preferred_language: str = Field(default="auto", min_length=2, max_length=16)


class TicketUpdate(BaseModel):
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None


class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    customer_id: int
    preferred_language: str = "en"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
