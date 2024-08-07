from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Index, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    items = relationship("Item", back_populates="owner")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    address = Column(String(500), index=True)
    city = Column(String(50), index=True)
    state = Column(String(50), index=True)
    zip = Column(String(25), index=True)
    phone = Column(String(50), index=True)
    email = Column(String(255), unique=True, index=True)
    special_instructions = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)
    schedules = relationship("Schedule", back_populates="client_rel")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    description = Column(String(255), index=True)
    purchased_date = Column(DateTime, index=True, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")


class CrewLeaders(Base):
    __tablename__ = "crew_leaders"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)
    list_order = Column(Integer, index=True)
    owned_crews = relationship("Crews", back_populates="owner")
    schedules = relationship("Schedule", back_populates="crew_leader")


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), index=True)
    address = Column(String(250), index=True)
    start = Column(DateTime, index=True, default=datetime.utcnow)
    end = Column(DateTime, index=True, default=datetime.utcnow)
    crew_leader_id = Column(Integer, ForeignKey('crew_leaders.id'))  # Foreign key referencing CrewLeader
    crew_leader = relationship("CrewLeaders", back_populates="schedules")
    client_id = Column(Integer, ForeignKey('clients.id'))  # Foreign key referencing Client
    client_rel = relationship("Client", back_populates="schedules")


class Crews(Base):
    __tablename__ = "crews"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    start_date = Column(DateTime, index=True, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("crew_leaders.id"))
    owner = relationship("CrewLeaders", back_populates="owned_crews")


class TimeOff(Base):
    __tablename__ = "time_off"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), index=True)
    start = Column(DateTime, index=True, default=datetime.utcnow)
    end = Column(DateTime, index=True, default=datetime.utcnow)


class Appointments(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), index=True)
    address = Column(String(250), index=True)
    phone = Column(String(250), index=True)
    start = Column(DateTime, index=True, default=datetime.utcnow)
    end = Column(DateTime, index=True, default=datetime.utcnow)
