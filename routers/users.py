import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import User, UserSession, session

router = APIRouter(prefix="/users")


class UserCredentials(BaseModel):
    username: str
    name: str | None
    password: str


def authenticate_user(credentials: UserCredentials) -> User:
    with session:
        stmt = select(User).where(User.username == credentials.username)
        user: User = session.scalar(stmt)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                headers={"WWW-Authenticate": "Basic"},
                detail="User not found",
            )

        if not user.verify_password(credentials.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )

        return user


def create_session(user_id: int):
    with session:
        user_session = UserSession(
            user_id=user_id, session_id=str(uuid.uuid4())
        )
        session.add(user_session)
        session.commit()
        session.refresh(user_session)

        return user_session.session_id


def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty session_id",
        )

    return session_id


def get_authenticated_user(request: Request):
    session_id = get_session_id(request)

    with session:
        stmt = select(UserSession).where(UserSession.session_id == session_id)
        user_session = session.scalar(stmt)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session_id",
            )

        user = get_user_from_session(user_session)
        return user


def get_user_from_session(user_session: UserSession):
    with session:
        stmt = select(User).where(User.id == user_session.user_id)
        user = session.scalar(stmt)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session_id",
            )

        return user


@router.get("/")
def get_users(user: User = Depends(get_authenticated_user)):
    if user.username not in os.environ["ADMINS"].split("|"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    with session:
        stmt = select(User)
        return [x.json() for x in session.scalars(stmt)]


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(data: UserCredentials):
    with session:
        try:
            user = User(**(dict(vars(data).items())))
            user.hash_password(data.password)
            session.add(user)
            session.commit()

            return {"message": "User created successfully"}
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: Request, user: User = Depends(authenticate_user)):
    if request.cookies.get("session_id"):
        with session:
            stmt = select(UserSession).where(
                UserSession.session_id == request.cookies.get("session_id")
            )
            user_session = session.scalar(stmt)
            if user_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User already logged in",
                )

    session_id = create_session(user.id)

    content = {
        "message": "User logged in successfully",
        "session_id": session_id,
    }
    response = JSONResponse(content=content)
    response.set_cookie(key="session_id", value=session_id)

    return response


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, session_id: str = Depends(get_session_id)):
    with session:
        stmt = select(UserSession).where(UserSession.session_id == session_id)
        user_session = session.scalar(stmt)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session_id",
            )
        session.delete(user_session)
        session.commit()

        response.delete_cookie(key="session_id")

        return {"message": "User logged out successfully"}


@router.get("/profile", status_code=status.HTTP_200_OK)
def get_profile(user: User = Depends(get_authenticated_user)):
    return user
