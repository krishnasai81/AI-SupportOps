from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Customer, User
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    customer_id: int | None


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    customer = db.query(Customer).filter(Customer.email == email).first()
    if customer is None:
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
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.model_validate(user).model_dump()}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": UserResponse.model_validate(user).model_dump()}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
