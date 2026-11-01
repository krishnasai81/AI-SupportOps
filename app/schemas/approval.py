from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecision(BaseModel):

    decision: Literal["approve", "reject"]

    reviewer_name: str = Field(
        min_length=2,
        max_length=100
    )

    review_note: str | None = Field(
        default=None,
        max_length=1000
    )


class ApprovalResponse(BaseModel):

    id: int
    ticket_id: int
    customer_id: int

    action_type: str
    requested_action: str
    reason: str

    status: str

    reviewer_name: str | None
    review_note: str | None

    created_at: datetime
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)