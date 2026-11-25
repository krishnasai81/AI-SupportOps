from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.approval import ApprovalDecision, ApprovalResponse
from app.security import require_roles
from app.services.approval_service import get_pending_approvals, decide_approval

router = APIRouter(prefix="/api/v1/approvals", tags=["Human Approvals"])


@router.get("/pending", response_model=list[ApprovalResponse])
def list_pending_approvals(
    db: Session = Depends(get_db),
    reviewer=Depends(require_roles("support", "admin")),
):
    return get_pending_approvals(db)


@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
def review_approval(
    approval_id: int,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    reviewer=Depends(require_roles("support", "admin")),
):
    try:
        approval = decide_approval(
            db=db,
            approval_id=approval_id,
            decision=payload.decision,
            reviewer_name=reviewer.email,
            review_note=payload.review_note,
        )
        if approval is None:
            raise HTTPException(status_code=404, detail="Approval request not found.")
        return approval
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
