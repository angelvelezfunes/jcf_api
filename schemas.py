# schemas.py
from typing import Union, Optional
from pydantic import BaseModel
from datetime import datetime


# ITEMS #
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    purchased_date: datetime


class ItemCreate(ItemBase):
    title: str
    description: Optional[str] = None
    purchased_date: datetime


class ItemRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    purchased_date: datetime


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


# CLIENTS #
class ClientCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    special_instructions: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True


class ClientRead(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    special_instructions: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state: Optional[str]
    is_active: bool

    class Config:
        orm_mode = True


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str]
    phone: Optional[str] = None
    address: Optional[str] = None
    special_instructions: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_active: Optional[bool] = None


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


# Schedule

class Schedule(BaseModel):
    id: int
    title: str
    address: str
    start: datetime
    end: datetime
    crew_leader_id: int


class ScheduleCreate(BaseModel):
    title: str
    address: str
    start: datetime
    end: datetime
    crew_leader_id: int


class ScheduleUpdate(BaseModel):
    id: int
    title: str
    address: str
    start: str
    end: str
    crew_leader_id: int


class ScheduleRead(BaseModel):
    id: int
    title: str
    address: Optional[str] = None
    start: datetime
    end: datetime
    crew_leader_id: Optional[int] = None

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
    address: str
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


class CrewUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    start_date: Optional[str]
    is_active: Optional[bool]
    owner_id: Optional[int]

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
