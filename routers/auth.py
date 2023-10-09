import os
import uuid

from fastapi import Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlmodel import select

from db import Owner, User, UserSession, session


class Credentials(BaseModel):
    username: str
    name: str | None
    password: str


def authenticate_user(
    credentials: Credentials, is_owner: bool = False
) -> User:
    """
    Authenticates a user with the given credentials.

    Args:
        credentials (Credentials): The user's credentials.
        is_owner (bool, optional): Whether the user is an owner. Defaults to False.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the user is not found or the password is incorrect.
    """
    Entity = Owner if is_owner else User

    with session:
        stmt = select(Entity).where(Entity.username == credentials.username)
        user: Entity = session.scalar(stmt)

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


def authenticate_owner(credentials: Credentials) -> Owner:
    return authenticate_user(credentials, is_owner=True)


def create_session(user_id: int, is_owner: bool = False):
    """
    Creates a new user session and returns the session ID.

    Args:
        user_id (int): The ID of the user for whom the session is being created.
        is_owner (bool, optional):
            Whether the user is the owner of the session.
            Defaults to False.

    Returns:
        str: The session ID of the newly created session.
    """
    with session:
        user_session = UserSession(
            user_id=user_id, session_id=str(uuid.uuid4()), is_owner=is_owner
        )
        session.add(user_session)
        session.commit()
        session.refresh(user_session)

        return user_session.session_id


def get_session_id(request: Request):
    """
    Returns the session ID from the request cookies.

    Args:
        request (Request): The request object.

    Raises:
        HTTPException: If the session ID is empty or not found in the cookies.

    Returns:
        str: The session ID.
    """
    session_id = request.cookies.get("session_id")
    if session_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty session_id",
        )

    return session_id


def get_authenticated_user(request: Request) -> User:
    """
    Returns the authenticated user for the given request.

    Args:
        request (Request): The incoming request.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the session_id is invalid.
    """
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


def get_authenticated_owner(request: Request) -> Owner:
    owner = get_authenticated_user(request)

    if not isinstance(owner, Owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return owner


def get_user_from_session(user_session: UserSession) -> User:
    """
    Given a UserSession object,
    returns the corresponding User or Owner object from the database.

    Args:
        user_session (UserSession):
            The UserSession object containing the user_id and is_owner flag.

    Returns:
        User or Owner:
            The User or Owner object corresponding to the user_id in the UserSession.

    Raises:
        HTTPException:
            If the user_id in the UserSession is invalid or
            does not correspond to a User or Owner object.
    """
    with session:
        Entity = Owner if user_session.is_owner else User

        stmt = select(Entity).where(Entity.id == user_session.user_id)
        user = session.scalar(stmt)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session_id",
            )

        return user


def is_already_logged_in(request: Request) -> bool:
    """
    Check if the user is already logged in
    by checking if the session_id cookie exists and is valid.

    Args:
        request (Request): The incoming request object.

    Returns:
        bool: True if the user is already logged in, False otherwise.
    """
    if request.cookies.get("session_id"):
        with session:
            stmt = select(UserSession).where(
                UserSession.session_id == request.cookies.get("session_id")
            )
            user_session = session.scalar(stmt)

            if user_session:
                return True

    return False


def get_admin_user(request: Request) -> User:
    """
    Returns the authenticated user if they are an admin user,
    otherwise raises a 403 Forbidden error.

    Args:
        request (Request): The request object.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the authenticated user is not an admin user.
    """
    user = get_authenticated_user(request)

    if user.username not in os.environ["ADMINS"].split(","):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user


def logout(response: Response, session_id: str = Depends(get_session_id)):
    """
    Logs out the user by deleting the user session from the database and
    deleting the session_id cookie from the response.

    Args:
        response (Response):
            The response object to delete the session_id cookie from.
        session_id (str, optional):
            The session ID to use for logging out.
            Defaults to Depends(get_session_id).

    Raises:
        HTTPException: If the session ID is invalid.

    Returns:
        dict: A dictionary containing a success message.
    """
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
