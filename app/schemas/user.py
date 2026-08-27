from typing import Literal

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserBioGenerated(BaseModel):
    headline: str
    bio: str
    tone: Literal["formal", "casual", "tecnico"]


class UserBioRead(UserBioGenerated):
    user_id: int
