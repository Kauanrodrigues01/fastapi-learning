from pydantic import BaseModel


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: str
    password: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: str


class UserDBSchema(BaseModel):
    id: int
    username: str
    email: str
    password: str


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]
