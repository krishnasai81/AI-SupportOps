from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Customer, User
from app.schemas.auth import UserPublic
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def auth_payload(user: User):
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": UserPublic.model_validate(user).model_dump(),
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    if db.query(Customer).filter(Customer.email == email).first():
        raise HTTPException(
            status_code=409,
            detail="This email is already associated with a customer record. Contact support to link it securely.",
        )
    try:
        customer = Customer(name=payload.name.strip(), email=email)
        db.add(customer)
        db.flush()
        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            role="customer",
            customer_id=customer.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return auth_payload(user)
    except Exception:
        db.rollback()
        raise


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return auth_payload(user)


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user
