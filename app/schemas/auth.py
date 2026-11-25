from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    customer_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
