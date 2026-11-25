import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Ticket
from app.security import get_current_user, require_ticket_access
from app.services.agent_service import process_ticket

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agents", tags=["AI Agent System"])


@router.post("/process-ticket/{ticket_id}")
async def process_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    require_ticket_access(ticket, user)
    try:
        result = await process_ticket(db=db, ticket_id=ticket_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Ticket not found.")
        return {"message": "Ticket processed successfully.", "result": result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Agent workflow failed for ticket %s", ticket_id)
        raise HTTPException(status_code=500, detail="Agent workflow failed. Check server logs.") from exc
