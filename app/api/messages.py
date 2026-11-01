
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.services.message_service import (
    add_message,
    get_ticket_messages
)


router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["Ticket Messages"]
)


class MessageCreate(BaseModel):
    sender_type: str
    message: str = Field(min_length=1)


@router.post("/{ticket_id}/messages")
def create_message(
    ticket_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    try:
        message = add_message(
            db,
            ticket_id,
            data.sender_type,
            data.message
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    if not message:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "id": message.id,
        "ticket_id": message.ticket_id,
        "sender_type": message.sender_type,
        "message": message.message,
        "created_at": message.created_at
    }


@router.get("/{ticket_id}/messages")
def list_messages(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    messages = get_ticket_messages(db, ticket_id)

    if not messages:
        from app.database.models import Ticket

        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id
        ).first()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

    return [
        {
            "id": message.id,
            "sender_type": message.sender_type,
            "message": message.message,
            "created_at": message.created_at
        }
        for message in messages
    ]
