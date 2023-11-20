from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
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


class SignupCredentials(UserCredentials):
    @validator("name")
    def validate_name(cls, name: str):
        if not name:
            raise ValueError("Name cannot be empty")

        return name

    @validator("username")
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
def get_profile(user: User = Depends(get_authenticated_user)):
    """
    Returns the JSON representation of the authenticated user's profile.

    Args:
        user (User): The authenticated user.

    Returns:
        dict: The JSON representation of the authenticated user's profile.
    """
    return user.json()


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
def sign_up(credentials: SignupCredentials):
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

            session.add(user)
            session.commit()

            session_id = create_session(user.id)
            response = JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "User created successfully",
                },
            )

            response.set_cookie(
                key="session_id",
                value=session_id,
                samesite="none",
                secure=True,
                httponly=False,
                expires=60 * 60 * 24 * 7,
            )

            return response
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username already exists",
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
        status_code=status.HTTP_200_OK,
        content={
            "message": "User logged in successfully",
        },
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        samesite="none",
        secure=True,
        httponly=False,
        expires=60 * 60 * 24 * 7,
    )

    return response


@router.put(
    "/profile",
    status_code=status.HTTP_200_OK,
)
def update_profile(
    credentials: UserCredentials, user: User = Depends(get_authenticated_user)
):
    """
    Updates the authenticated user's profile.

    Args:
        data (UserCredentials): The user credentials.

    Returns:
        dict: A dictionary containing a success message.
    """
    with session:
        for key, value in dict(vars(credentials).items()).items():
            if value:
                if key == "password":
                    value = User.hash_password(value)
                setattr(user, key, value)

        session.add(user)
        session.commit()

        return {"message": "User updated successfully", "user": user.json()}


router.add_api_route(
    path="/logout",
    endpoint=logout,
    methods=["POST"],
    status_code=status.HTTP_200_OK,
)
