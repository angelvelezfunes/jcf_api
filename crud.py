# crud.py
from typing import Optional
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload
import models
import schemas
from passlib.context import CryptContext
from sqlalchemy.sql import text
from sqlalchemy import or_

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


# USERS #
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_schedule_by_id(db: Session, id: int):
    return db.query(models.Schedule).filter(models.Schedule.id == id).first()


def get_users(db: Session, is_active: Optional[bool] = None):
    query = db.query(models.User)
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    return query.all()


def get_crew_leaders(db: Session, is_active: Optional[bool] = None):
    query = db.query(models.CrewLeaders)
    if is_active is not None:
        query = query.filter(models.CrewLeaders.is_active == is_active)
        query = query.order_by(models.CrewLeaders.first_name.asc())
    return query.all()


def get_schedule(db: Session):
    return db.query(models.Schedule).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username,
                          email=user.email,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          hashed_password=hashed_password,
                          is_admin=user.is_admin,
                          )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: models.User, user: schemas.UserUpdate):
    if user.password:
        hashed_password = get_password_hash(user.password)
        db_user.hashed_password = hashed_password

    if user.username:
        db_user.username = user.username

    if user.email:
        db_user.email = user.email

    if user.first_name:
        db_user.first_name = user.first_name

    if user.last_name:
        db_user.last_name = user.last_name

    if user.is_active is not None:
        db_user.is_active = user.is_active

    db.commit()
    db.refresh(db_user)
    return db_user


# CLIENTS #
def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(
                              first_name=client.first_name,
                              last_name=client.last_name,
                              phone=client.phone,
                              address=client.address,
                              city=client.city,
                              state=client.state,
                              zip=client.zip,
                              special_instructions=client.special_instructions,
                              )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_clients(db: Session):
    return db.query(models.Client).filter(models.Client.is_active == True).order_by(models.Client.first_name, models.Client.last_name).all()


# ITEMS #

def get_inventory(db: Session, skip: int = 0):
    return db.query(models.Item).offset(skip).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_schedule(db: Session, schedule: schemas.ScheduleCreate):
    db_schedule = models.Schedule(
        title=schedule.title,
        address=schedule.address,
        start=schedule.start,
        end=schedule.end,
        crew_leader_id=schedule.crew_leader_id,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def create_crew_leader(db: Session, crew_leader: schemas.CrewLeaderCreate):
    db_crew_leader = models.CrewLeaders(
        first_name=crew_leader.first_name,
        last_name=crew_leader.last_name,
        is_active=crew_leader.is_active
    )
    db.add(db_crew_leader)
    db.commit()
    db.refresh(db_crew_leader)
    return db_crew_leader


def get_crews(db: Session):
    return db.query(models.Crews).join(models.CrewLeaders).order_by(asc(models.CrewLeaders.first_name)).options(
        joinedload(models.Crews.owner)
    ).all()


def get_crew(db: Session, crew_id: int):
    return db.query(models.Crews).filter(models.Crews.id == crew_id).first()


def update_crew(db: Session, crew_id: int, crew_update: schemas.CrewUpdate):
    db_crew = db.query(models.Crews).filter(models.Crews.id == crew_id).first()
    if db_crew:
        for key, value in crew_update.dict(exclude_unset=True).items():
            setattr(db_crew, key, value)
        db.commit()
        db.refresh(db_crew)
    return db_crew


def update_crew_leader(db: Session, crew_leader_id: int, crew_leader_update: schemas.CrewLeaderUpdate):
    db_crew_leader = db.query(models.CrewLeaders).filter(models.CrewLeaders.id == crew_leader_id).first()
    if not db_crew_leader:
        return None
    for key, value in crew_leader_update.dict(exclude_unset=True).items():
        setattr(db_crew_leader, key, value)
    db.commit()
    db.refresh(db_crew_leader)
    return db_crew_leader


def get_schedules_by_crew_leader(db: Session, crew_leader_id: int):
    return db.query(models.Schedule).filter(models.Schedule.crew_leader_id == crew_leader_id).all()


def delete_schedule(db: Session, schedule_id: int):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if schedule:
        db.delete(schedule)
        db.commit()
        return True
    return False


def create_crew(db: Session, crews: schemas.CrewCreate):
    db_crew = models.Crews(
        first_name=crews.first_name,
        last_name=crews.last_name,
        start_date=crews.start_date,
        is_active=crews.is_active,
        owner_id=crews.owner_id
    )
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)
    return db_crew


def get_crews_by_crew_leader(db: Session, crew_leader_id: int):
    return db.query(models.Crews).filter(models.Crews.owner_id == crew_leader_id).all()


def get_schedule_by_date(db: Session, date: str):
    # noinspection SqlResolve
    sql_query = """
           SELECT *
           FROM inventory.schedule s
           JOIN inventory.crew_leaders c ON s.crew_leader_id = c.id
           WHERE DATE(s.start) = :date
           ORDER BY c.id, s.start asc
       """
    schedule = db.execute(text(sql_query), {"date": date}).fetchall()
    return schedule


def create_time_off(db: Session, time_off: schemas.TimeOffCreate):
    db_time_off = models.TimeOff(
        name=time_off.name,
        start=time_off.start,
        end=time_off.end
    )
    db.add(db_time_off)
    db.commit()
    db.refresh(db_time_off)
    return db_time_off


def delete_time_off(db: Session, time_off_id: int):
    time_off = db.query(models.TimeOff).filter(models.TimeOff.id == time_off_id).first()
    if time_off:
        db.delete(time_off)
        db.commit()
        return True
    return False


def get_time_off_by_id(db: Session, id: int):
    return db.query(models.TimeOff).filter(models.TimeOff.id == id).first()


def get_appointment_by_id(db: Session, id: int):
    return db.query(models.Appointments).filter(models.Appointments.id == id).first()


def get_time_off(db: Session):
    return db.query(models.TimeOff).all()


def get_time_off_by_date(db: Session, date_start: str, date_end: str):
    # noinspection SqlResolve
    sql_query = """
            SELECT id, name, DATE_FORMAT(start, '%m/%d/%Y %k:%i:%s') AS start, 
                       DATE_FORMAT(end, '%m/%d/%Y %k:%i:%s') AS end
           FROM inventory.time_off s
           WHERE s.start BETWEEN :start AND :end 
       """
    schedule = db.execute(text(sql_query), {"start": date_start, "end": date_end}).fetchall()
    return schedule


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointments(
        name=appointment.name,
        start=appointment.start,
        end=appointment.end,
        phone=appointment.phone,
        address=appointment.address,
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def get_appointments(db: Session):
    return db.query(models.Appointments).all()


def delete_appointment(db: Session, appointment_id: int):
    appointment = db.query(models.Appointments).filter(models.Appointments.id == appointment_id).first()
    if appointment:
        db.delete(appointment)
        db.commit()


def update_client(db: Session, client_id: int, db_client_update: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        return None
    for key, value in db_client_update.dict(exclude_unset=True).items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_clients_top_20(db: Session, query: str = "", skip: int = 0, limit: int = 20):
    if query:
        return db.query(models.Client).filter(
            or_(
                models.Client.first_name.ilike(f"%{query}%"),
                models.Client.last_name.ilike(f"%{query}%"),
                models.Client.address.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit).all()
    else:
        return db.query(models.Client).offset(skip).limit(limit).all()
