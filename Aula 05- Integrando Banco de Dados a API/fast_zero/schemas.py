from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserDBSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]
