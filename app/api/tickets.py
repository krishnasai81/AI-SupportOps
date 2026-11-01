from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse
)

from app.services import ticket_service


router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["Tickets"]
)


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db)
):

    return ticket_service.create_ticket(db, ticket)


@router.get(
    "/",
    response_model=list[TicketResponse]
)
def get_tickets(db: Session = Depends(get_db)):

    return ticket_service.get_all_tickets(db)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):

    ticket = ticket_service.get_ticket_by_id(
        db,
        ticket_id
    )

    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse
)
def update_existing_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: Session = Depends(get_db)
):

    ticket = ticket_service.update_ticket(
        db,
        ticket_id,
        update_data
    )

    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket