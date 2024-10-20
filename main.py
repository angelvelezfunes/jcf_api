from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
import models
from models import User
import crud
import schemas
from database import SessionLocal, engine, Base
import middleware
from mangum import Mangum

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
handler = Mangum(app)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://jcfmaintenance.com",
    "https://jcfmaintenance.com/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Load environment variables from .env file
load_dotenv()

# Get environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE"))

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(middleware.AuthMiddleware, db=SessionLocal(), secret_key=SECRET_KEY, algorithm=ALGORITHM)


@app.get("/")
async def root():
    return {"message": "Hi, Users"}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password or inactive account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }


# USERS
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.put("/users/{id}", response_model=schemas.User)
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user_with_same_username = crud.get_user_by_username(db, username=user.username)
    if db_user_with_same_username and db_user_with_same_username.id != id:
        raise HTTPException(status_code=400, detail="Username already registered")

    return crud.update_user(db=db, db_user=db_user, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(is_active: Optional[bool] = None, db: Session = Depends(get_db)):
    users = crud.get_users(db, is_active=is_active)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


# CLIENT
@app.post("/clients", response_model=list[schemas.ClientCreate])
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    crud.create_client(db=db, client=client)
    clients = crud.get_clients(db)
    return clients


@app.put("/clients/{client_id}", response_model=schemas.ClientRead)
def update_client(client_id: int, db_client_update: schemas.ClientUpdate, db: Session = Depends(get_db)):
    db_client_update = crud.update_client(db=db, client_id=client_id, db_client_update=db_client_update)
    if not db_client_update:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client_update


@app.get("/clients", response_model=list[schemas.ClientRead])
def read_clients(db: Session = Depends(get_db)):
    clients = crud.get_clients(db)
    return clients


@app.get("/clients-top-30", response_model=list[schemas.ClientRead])
async def get_clients_top_30(query: str = "", skip: int = 0, limit: int = 30, db: Session = Depends(get_db)):
    items = crud.get_clients_top_30(db, query=query, skip=skip, limit=limit)
    return items


@app.delete("/clients/{client_id}", response_model=schemas.ClientRead)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client_by_id(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    crud.delete_client(db, client_id)
    return client


# ITEMS
@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = 0  # = crud.get_items(db, skip=skip, limit=limit)
    return items


# Schedule
@app.post("/schedule", response_model=schemas.Schedule)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = crud.create_schedule(db=db, schedule=schedule)
    return db_schedule


@app.get("/schedule", response_model=list[schemas.ScheduleRead])
def read_schedules(db: Session = Depends(get_db)):
    schedule = crud.get_schedule(db)
    return schedule


@app.get("/schedule-get-history", response_model=list[schemas.ScheduleSearch])
def read_schedules_history(title: str, db: Session = Depends(get_db)):
    schedule = crud.get_schedule_history(db, title=title)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule history not found")
    return schedule


@app.delete("/schedule/{schedule_id}", response_model=schemas.ScheduleRead)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """
    Delete a schedule by ID.
    """
    schedule = crud.get_schedule_by_id(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    crud.delete_schedule(db, schedule_id)
    return schedule


# Crew Leader
@app.post("/crewLeader", response_model=schemas.CrewLeaderRead)
def create_crew_leader(crew_leader: schemas.CrewLeaderCreate, db: Session = Depends(get_db)):
    db_crew_leader = crud.create_crew_leader(db=db, crew_leader=crew_leader)
    return db_crew_leader


@app.get("/crewLeaders", response_model=list[schemas.CrewLeaderRead])
def read_crew_leaders(is_active: Optional[bool] = None, db: Session = Depends(get_db)):
    crew_leaders = crud.get_crew_leaders(db, is_active=is_active)
    return crew_leaders


@app.put("/crewLeader/{crew_leader_id}", response_model=schemas.CrewLeaderRead)
def update_crew_leader(crew_leader_id: int, crew_leader_update: schemas.CrewLeaderUpdate,
                       db: Session = Depends(get_db)):
    db_crew_leader = crud.update_crew_leader(db=db, crew_leader_id=crew_leader_id,
                                             crew_leader_update=crew_leader_update)
    if not db_crew_leader:
        raise HTTPException(status_code=404, detail="Crew Leader not found")
    return db_crew_leader


@app.get("/schedules/{crew_leader_id}", response_model=list[schemas.ScheduleRead])
def read_schedules(crew_leader_id: int, db: Session = Depends(get_db)):
    return crud.get_schedules_by_crew_leader(db=db, crew_leader_id=crew_leader_id)


# Crews
@app.post("/crews", response_model=schemas.CrewCreate)
def create_schedule(crews: schemas.CrewCreate, db: Session = Depends(get_db)):
    db_schedule = crud.create_crew(db=db, crews=crews)
    return db_schedule


@app.put("/crews/{crew_id}", response_model=schemas.CrewRead)
def update_crew(crew_id: int, crew_update: schemas.CrewUpdate,
                db: Session = Depends(get_db)):
    db_crew = crud.get_crew(db, crew_id)
    if db_crew is None:
        raise HTTPException(status_code=404, detail="Crew not found")

    db_crew = crud.update_crew(db=db, crew_id=crew_id, crew_update=crew_update)
    return db_crew


@app.get("/crews", response_model=list[schemas.CrewRead])
def read_crew_leaders(db: Session = Depends(get_db)):
    crews = crud.get_crews(db)
    return crews


@app.get("/crews/{crew_leader_id}", response_model=list[schemas.CrewRead])
def read_schedules(crew_leader_id: int, db: Session = Depends(get_db)):
    return crud.get_crews_by_crew_leader(db=db, crew_leader_id=crew_leader_id)


@app.get("/scheduleCrews", response_model=list[schemas.CrewLeaderSchedule])
def get_schedule_by_date(date: str, db: Session = Depends(get_db)):
    if date is not None:
        schedule = crud.get_schedule_by_date(db, date)
    else:
        # If date is not provided, return the complete schedule
        schedule = crud.get_schedule(db)

    return schedule


@app.put("/schedule/{schedule_id}", response_model=schemas.ScheduleRead)
def update_schedule(schedule_id: int, schedule_update: schemas.ScheduleUpdate, db: Session = Depends(get_db)):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for key, value in schedule_update.dict(exclude_unset=True).items():
        setattr(db_schedule, key, value)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


# Time Off
@app.post("/time-off", response_model=schemas.TimeOffRead)
def create_time_off_endpoint(time_off: schemas.TimeOffCreate, db: Session = Depends(get_db)):
    db_time_off = crud.create_time_off(db=db, time_off=time_off)
    return db_time_off


@app.get("/time-off", response_model=list[schemas.TimeOffRead])
def read_time_off(db: Session = Depends(get_db)):
    time_off = crud.get_time_off(db)
    return time_off


@app.delete("/time-off/{time_off_id}", response_model=schemas.TimeOffRead)
def delete_time_off_endpoint(time_off_id: int, db: Session = Depends(get_db)):
    time_off = crud.get_time_off_by_id(db, time_off_id)
    if time_off is None:
        raise HTTPException(status_code=404, detail="Time off not found")
    crud.delete_time_off(db, time_off_id)
    return time_off


@app.get("/time-off-Crews", response_model=list[schemas.TimeOffReadFormatted])
def time_off_by_date(date_start: str, date_end: str, db: Session = Depends(get_db)):
    schedule = crud.get_time_off_by_date(db, date_start, date_end)

    return schedule


# Appointments
@app.post("/appointments", response_model=schemas.AppointmentCreate)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = crud.create_appointment(db=db, appointment=appointment)
    return db_appointment


@app.get("/appointments", response_model=list[schemas.AppointmentRead])
def read_appointments(db: Session = Depends(get_db)):
    appointments = crud.get_appointments(db)
    return appointments


@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentUpdate)
def update_appointments(appointment_id: int, db_appointment_update: schemas.AppointmentUpdate,
                        db: Session = Depends(get_db)):
    db_appointment_update = crud.update_appointment(db=db, appointment_id=appointment_id,
                                                    db_appointment_update=db_appointment_update)
    if not db_appointment_update:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment_update


@app.delete("/appointments/{appointment_id}", response_model=schemas.AppointmentRead)
def delete_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = crud.get_appointment_by_id(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    crud.delete_appointment(db, appointment_id)
    return appointment


# Items
@app.get("/inventory", response_model=list[schemas.ItemRead])
def read_inventory(db: Session = Depends(get_db)):
    inventory = crud.get_inventory(db)
    return inventory


@app.post("/send-email-reminder")
def send_email_reminder(db: Session = Depends(get_db)):
    crud.send_estimate_reminder(db)

    return {"msg": "send reminder"}
