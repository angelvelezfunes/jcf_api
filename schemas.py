# schemas.py
from typing import Union
from pydantic import BaseModel


# ITEMS #
class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# USERS #

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    name: str
    email: str
    username: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True


# CLIENTS #
class ClientCreate(UserBase):
    first_name: str
    last_name: str
    phone: str
    address: str
    name: str
    special_instructions: str
    zip: str
    city: str
    state: str
    is_active: bool


class Client(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True