from dataclasses import dataclass
from typing import Optional
import bcrypt
from fastapi import APIRouter, status, HTTPException
from db import session, Owner
from sqlmodel import select
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/owners")


@dataclass
class OwnerCredentials:
    username: str
    name: str
    password: str

    email: Optional[str]
    phone_number: Optional[str]
    instagram: Optional[str]

    def __post_init__(self):
        self.password = bcrypt.hashpw(
            self.password.encode(), bcrypt.gensalt()
        ).decode()


@router.get("/")
def get_owners():
    with session:
        stmt = select(Owner)
        return session.scalar(stmt)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_owner(data: OwnerCredentials):
    with session:
        try:
            owner = Owner(**(dict(vars(data).items())))
            session.add(owner)
            session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
