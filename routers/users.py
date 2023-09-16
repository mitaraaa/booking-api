from dataclasses import dataclass
import bcrypt
from fastapi import APIRouter, status, HTTPException
from db import session, User
from sqlmodel import select
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/users")


@dataclass
class UserCredentials:
    username: str
    name: str
    password: str

    def __post_init__(self):
        self.password = bcrypt.hashpw(
            self.password.encode(), bcrypt.gensalt()
        ).decode()


@router.get("/")
def get_users():
    with session:
        stmt = select(User)
        return session.scalar(stmt)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCredentials):
    with session:
        try:
            user = User(**(dict(vars(data).items())))
            session.add(user)
            session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
