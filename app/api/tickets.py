from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.security import get_current_user, require_roles, require_ticket_access
from app.services import ticket_service
from app.services.translation_service import normalize_ticket

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        translated = await normalize_ticket(
            payload.subject, payload.description, payload.preferred_language
        )
        owner_customer_id = user.customer_id if user.role == "customer" else None
        ticket = ticket_service.create_ticket(
            db,
            payload,
            owner_customer_id=owner_customer_id,
            normalized_subject=translated["normalized_subject"],
            normalized_description=translated["normalized_description"],
            detected_language=translated["detected_language"],
        )
        return ticket
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/", response_model=list[TicketResponse])
def get_tickets(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(Ticket)
    if user.role == "customer":
        query = query.filter(Ticket.customer_id == user.customer_id)
    return query.order_by(Ticket.created_at.desc()).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    require_ticket_access(ticket, user)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("support", "admin")),
):
    ticket = ticket_service.update_ticket(db, ticket_id, update_data)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return ticket
