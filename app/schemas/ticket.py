from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

from app.database.models import (
    TicketCategory,
    TicketPriority,
    TicketStatus
)


class TicketCreate(BaseModel):

    customer_name: str = Field(min_length=2, max_length=100)

    customer_email: EmailStr

    subject: str = Field(min_length=5, max_length=200)

    description: str = Field(min_length=10)


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

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)