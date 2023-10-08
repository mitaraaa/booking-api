from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import Owner, session
from routers.auth import (
    authenticate_user,
    create_session,
    get_admin_user,
    get_authenticated_user,
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


@router.get("/", dependencies=[Depends(get_admin_user)])
def get_owners():
    with session:
        stmt = select(Owner)
        return session.scalar(stmt)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_user)],
)
def create_owner(credentials: OwnerCredentials):
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


@router.get(
    "/{owner_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_admin_user)],
)
def get_owner(owner_id: int):
    with session:
        stmt = select(Owner).where(Owner.id == owner_id)
        owner = session.scalar(stmt)

        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return session.scalar(stmt)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: Request, owner: Owner = Depends(authenticate_user)):
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
    response.set_cookie(key="session_id", value=session_id)

    return response


@router.get("/profile", status_code=status.HTTP_200_OK)
def get_profile(owner: Owner = Depends(get_authenticated_user)):
    return owner.json()


@router.put("/profile", status_code=status.HTTP_200_OK)
def update_profile(
    credentials: OwnerCredentials,
    owner: Owner = Depends(get_authenticated_user),
):
    with session:
        for key, value in dict(vars(credentials).items()):
            if value:
                if key == "password":
                    value = Owner.hash_password(value)
                setattr(owner, key, value)

        session.add(owner)
        session.commit()

        return {
            "message": "User updated successfully",
            "user": owner.json(),
        }


router.add_api_route(
    path="/logout",
    endpoint=logout,
    methods=["POST"],
    status_code=status.HTTP_200_OK,
)
