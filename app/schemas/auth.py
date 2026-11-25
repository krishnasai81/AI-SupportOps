from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    customer_id: int | None

    class Config:
        from_attributes = True
