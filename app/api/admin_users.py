from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.security import hash_password, require_roles

router = APIRouter(prefix="/api/v1/admin/users", tags=["User Administration"])


class AccountCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


@router.post("/support", status_code=status.HTTP_201_CREATED)
def create_support_user(
    payload: AccountCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_roles("admin")),
):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(email=email, password_hash=hash_password(payload.password), role="support", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}
