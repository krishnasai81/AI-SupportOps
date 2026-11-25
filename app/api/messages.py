from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Ticket
from app.security import get_current_user, require_ticket_access
from app.services.message_service import add_message, get_ticket_messages

router = APIRouter(prefix="/api/v1/tickets", tags=["Ticket Messages"])


class MessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


@router.post("/{ticket_id}/messages")
def create_message(
    ticket_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    require_ticket_access(ticket, user)
    sender_type = "customer" if user.role == "customer" else "support"
    message = add_message(db, ticket_id, sender_type, data.message)
    return {
        "id": message.id,
        "ticket_id": message.ticket_id,
        "sender_type": message.sender_type,
        "message": message.message,
        "created_at": message.created_at,
    }


@router.get("/{ticket_id}/messages")
def list_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    require_ticket_access(ticket, user)
    return [
        {
            "id": message.id,
            "sender_type": message.sender_type,
            "message": message.message,
            "created_at": message.created_at,
        }
        for message in get_ticket_messages(db, ticket_id)
    ]
