from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import Owner, session
from routers.auth import (
    authenticate_owner,
    create_session,
    get_admin_user,
    get_authenticated_owner,
    is_already_logged_in,
    logout,
)

router = APIRouter(prefix="/owners")


class OwnerCredentials(BaseModel):
    username: str | None
    name: str | None
    password: str | None

    email: Optional[str]
    phone_number: Optional[str]
    instagram: Optional[str]


class SignupCredentials(OwnerCredentials):
    @validator("name")
    def validate_name(cls, name: str):
        if not name:
            raise ValueError("Name cannot be empty")

        return name

    def validate_username(cls, username: str):
        allowed_characters = ["_", "."]

        if not username:
            raise ValueError("Username cannot be empty")

        if len(username) < 2:
            raise ValueError("Username must be at least 3 characters long")

        if username.isnumeric():
            raise ValueError("Username cannot be numeric")

        if not username.isalnum():
            raise ValueError("Username must be alphanumeric")

        if any(
            x not in allowed_characters for x in username if not x.isalnum()
        ):
            raise ValueError(
                "Username must only contain alphanumeric characters, underscores, and periods"
            )

        return username

    @validator("password")
    def validate_password(cls, password: str):
        if not password:
            raise ValueError("Password cannot be empty")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not password.isalnum():
            raise ValueError("Password must be alphanumeric")

        return password


@router.get("/profile", status_code=status.HTTP_200_OK)
def get_profile(owner: Owner = Depends(get_authenticated_owner)):
    return owner.json()


@router.get("/")
def get_owners():
    with session:
        stmt = select(Owner)
        return [owner.json() for owner in session.scalars(stmt)]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_user)],
)
def create_owner(credentials: SignupCredentials):
    with session:
        try:
            credentials.password = Owner.hash_password(credentials.password)
            owner = Owner(**(dict(vars(credentials).items())))

            session.add(owner)
            session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        return {"message": "Owner created successfully"}


@router.get(
    "/{owner_id}",
    status_code=status.HTTP_200_OK,
)
def get_owner(owner_id: int):
    with session:
        stmt = select(Owner).where(Owner.id == owner_id)
        owner = session.scalar(stmt)

        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return owner.json()


@router.delete(
    "/{owner_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_admin_user)],
)
def delete_owner(owner_id: int):
    with session:
        stmt = select(Owner).where(Owner.id == owner_id)
        owner = session.scalar(stmt)

        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        session.delete(owner)
        session.commit()

        return {"message": "Owner deleted successfully"}


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: Request, owner: Owner = Depends(authenticate_owner)):
    if is_already_logged_in(request):
        return JSONResponse(
            content={"message": "User already logged in"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    session_id = create_session(owner.id, is_owner=True)
    response = JSONResponse(
        content={
            "message": "User logged in successfully",
            "session_id": session_id,
        },
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        samesite="none",
        secure=True,
        httponly=True,
        expires=60 * 60 * 24 * 7,
    )

    return response


@router.put("/profile", status_code=status.HTTP_200_OK)
def update_profile(
    credentials: OwnerCredentials,
    owner: Owner = Depends(get_authenticated_owner),
):
    with session:
        for key, value in dict(vars(credentials).items()).items():
            if value:
                if key == "username":
                    continue
                if key == "password":
                    value = Owner.hash_password(value)
                setattr(owner, key, value)

        session.add(owner)
        session.commit()

        return {
            "message": "Profile updated successfully",
            "user": owner.json(),
        }


router.add_api_route(
    path="/logout",
    endpoint=logout,
    methods=["POST"],
    status_code=status.HTTP_200_OK,
)
