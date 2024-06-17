# schemas.py
from typing import Union, Optional
from pydantic import BaseModel
from datetime import datetime


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
        from_attributes = True


# USERS #

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool


class UserUpdate(UserBase):
    username: str
    password: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    is_admin: Optional[bool] = None
    is_active: Optional[bool]


class User(UserBase):
    id: int
    is_active: bool
    username: str
    first_name: str
    last_name: str
    email: str
    items: list[Item] = []

    class Config:
        from_attributes = True


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


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str = None

    class Config:
        from_attributes = True


class Client(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# Schedule
class ScheduleCreate(BaseModel):
    title: str
    start: datetime
    end: datetime
    crew_leader_id: int


class ScheduleRead(BaseModel):
    id: int
    title: str
    start: datetime
    end: datetime
    crew_leader_id: int

    class Config:
        orm_mode = True


class CrewLeaderCreate(BaseModel):
    first_name: str
    last_name: str
    is_active: bool


class CrewLeaderRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        orm_mode = True


class CrewLeaderUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: Optional[bool]


class CrewLeaderWithSchedules(CrewLeaderRead):
    schedules: list[ScheduleRead] = []


class CrewRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    is_active: bool
    owner_id: int
    owner: CrewLeaderRead
    start_date: datetime

    class Config:
        orm_mode = True


class CrewLeaderSchedule(BaseModel):
    id: int
    first_name: str
    last_name: str
    title: str
    start: datetime
    end: datetime

    # owner: Optional[list[CrewLeaderRead]] = None

    class Config:
        orm_mode = True


class CrewCreate(BaseModel):
    first_name: str
    last_name: str
    start_date: datetime
    is_active: bool
    owner_id: int


# Time Off
class TimeOffCreate(BaseModel):
    name: str
    start: datetime
    end: datetime


class TimeOffRead(BaseModel):
    id: int
    name: str
    start: datetime
    end: datetime

    class Config:
        orm_mode = True


class TimeOffReadFormatted(BaseModel):
    id: int
    name: str
    start: str
    end: str

    class Config:
        orm_mode = True


# Appointment
class AppointmentCreate(BaseModel):
    name: str
    start: datetime
    end: datetime
    phone: str
    address: str

    class Config:
        orm_mode = True


class AppointmentRead(BaseModel):
    id: int
    name: str
    start: datetime
    end: datetime
    phone: str
    address: str

    class Config:
        orm_mode = True
