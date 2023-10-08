from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import User, session
from routers.auth import (
    authenticate_user,
    create_session,
    get_admin_user,
    get_authenticated_user,
    is_already_logged_in,
    logout,
)

router = APIRouter(prefix="/users")


class UserCredentials(BaseModel):
    """
    Represents the credentials of a user.

    Attributes:
        username (str): The username of the user.
        name (str, optional): The name of the user.
        password (str): The password of the user.
    """

    username: str | None
    name: str | None
    password: str | None


@router.get("/", dependencies=[Depends(get_admin_user)])
def get_users():
    """
    Retrieve all users.

    Returns:
        List[dict]: A list of dictionaries containing user information.
    """
    with session:
        stmt = select(User)
        return [x.json() for x in session.scalars(stmt)]


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_admin_user)],
)
def get_user(user_id: int):
    """
    Retrieve a user by ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: A dictionary containing user information.
    """
    with session:
        stmt = select(User).where(User.id == user_id)
        user = session.scalar(stmt)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return user.json()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(credentials: UserCredentials):
    """
    Creates a new user in the database.

    Args:
        data (UserCredentials): The user credentials.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException:
            If the user already exists in the database or
            if the user credentials are invalid.
    """
    with session:
        try:
            credentials.password = User.hash_password(credentials.password)
            user = User(**(dict(vars(credentials).items())))
            user.hash_password(credentials.password)
            session.add(user)
            session.commit()

            return {"message": "User created successfully"}
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: Request, user: User = Depends(authenticate_user)):
    """
    Logs in a user and creates a session for them.

    Args:
        request (Request): The incoming request.
        user (User): The authenticated user.

    Returns:
        JSONResponse: A JSON response containing a message and session ID cookie.
    """
    if is_already_logged_in(request):
        return JSONResponse(
            content={"message": "User already logged in"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    session_id = create_session(user.id)
    response = JSONResponse(
        content={
            "message": "User logged in successfully",
            "session_id": session_id,
        }
    )
    response.set_cookie(key="session_id", value=session_id)

    return response


@router.get("/profile", status_code=status.HTTP_200_OK)
def get_profile(user: User = Depends(get_authenticated_user)):
    """
    Returns the JSON representation of the authenticated user's profile.

    Args:
        user (User): The authenticated user.

    Returns:
        dict: The JSON representation of the authenticated user's profile.
    """
    return user.json()


@router.put(
    "/profile",
    status_code=status.HTTP_200_OK,
)
def update_profile(
    data: UserCredentials, user: User = Depends(get_authenticated_user)
):
    """
    Updates the authenticated user's profile.

    Args:
        data (UserCredentials): The user credentials.

    Returns:
        dict: A dictionary containing a success message.
    """
    with session:
        if data.name:
            user.name = data.name

        if data.password:
            user.password = User.hash_password(data.password)

        session.add(user)
        session.commit()

        return {"message": "User updated successfully", "user": user.json()}


router.add_api_route(
    path="/logout",
    endpoint=logout,
    methods=["POST"],
    status_code=status.HTTP_200_OK,
)
