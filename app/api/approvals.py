import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.schemas.approval import ApprovalDecision, ApprovalResponse
from app.services.approval_service import (
    get_pending_approvals,
    get_approval_by_id,
    decide_approval,
)

router = APIRouter(
    prefix="/api/v1/approvals",
    tags=["Human Approvals"],
)


class ApprovalLogin(BaseModel):
    api_key: str


def verify_approval_key(
    x_approval_key: str = Header(...),
):
    configured_key = settings.APPROVAL_API_KEY

    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail="Approval API key is not configured.",
        )

    expected_key = configured_key.get_secret_value()

    if not secrets.compare_digest(x_approval_key, expected_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid approval API key.",
        )

    return True


def require_admin_session(request: Request):
    if not request.session.get("approval_authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Please authenticate to access approvals.",
        )


# Session authentication
@router.post("/session")
def create_approval_session(
    payload: ApprovalLogin,
    request: Request,
):
    configured_key = settings.APPROVAL_API_KEY

    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail="Approval authentication is not configured.",
        )

    expected_key = configured_key.get_secret_value()

    if not secrets.compare_digest(payload.api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid approval key.",
        )

    request.session["approval_authenticated"] = True

    return {"authenticated": True}


@router.delete("/session")
def delete_approval_session(request: Request):
    request.session.clear()
    return {"authenticated": False}


# Session-protected admin routes
@router.get(
    "/admin/pending",
    response_model=list[ApprovalResponse],
)
def get_admin_pending_approvals(
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin_session(request)
    return get_pending_approvals(db)


@router.post(
    "/admin/{approval_id}/decision",
    response_model=ApprovalResponse,
)
def make_admin_approval_decision(
    approval_id: int,
    payload: ApprovalDecision,
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin_session(request)

    try:
        approval = decide_approval(
            db=db,
            approval_id=approval_id,
            decision=payload.decision,
            reviewer_name=payload.reviewer_name,
            review_note=payload.review_note,
        )

        if not approval:
            raise HTTPException(
                status_code=404,
                detail="Approval request not found.",
            )

        return approval

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


# API-key-protected routes
@router.get(
    "/pending",
    response_model=list[ApprovalResponse],
)
def list_pending_approvals(
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_approval_key),
):
    return get_pending_approvals(db)


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_approval_key),
):
    approval = get_approval_by_id(db, approval_id)

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found.",
        )

    return approval


@router.post(
    "/{approval_id}/decision",
    response_model=ApprovalResponse,
)
def review_approval(
    approval_id: int,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_approval_key),
):
    try:
        approval = decide_approval(
            db=db,
            approval_id=approval_id,
            decision=payload.decision,
            reviewer_name=payload.reviewer_name,
            review_note=payload.review_note,
        )

        if not approval:
            raise HTTPException(
                status_code=404,
                detail="Approval request not found.",
            )

        return approval

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc