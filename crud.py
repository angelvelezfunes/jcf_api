# crud.py
from sqlalchemy.orm import Session
import models
import schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


# USERS #
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email,
                          name=user.name,
                          username=user.username,
                          hashed_password=fake_hashed_password,
                          )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# CLIENTS #

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(email=client.email,
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


def get_client_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.Client.email == email).first()


# ITEMS #

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
