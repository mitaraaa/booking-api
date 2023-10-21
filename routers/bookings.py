from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import Booking, FootballField, Owner, User, session
from db.models.booking import BookingStatus
from routers.auth import (
    get_admin_user,
    get_authenticated_owner,
    get_authenticated_user,
    is_admin,
)

router = APIRouter(prefix="/bookings")


class BookingData(BaseModel):
    user_id: int | None
    field_id: int | None

    booking_date: datetime | None
    booked_until: datetime | None

    status: BookingStatus | None = BookingStatus.pending


class BookingUpdate(BaseModel):
    status: BookingStatus


def overlap(booking: Booking) -> bool:
    with session:
        stmt = select(Booking).where(
            Booking.field_id == booking.field_id,
        )

        existing_bookings: list[Booking] = session.scalars(stmt)

        for existing_booking in existing_bookings:
            if (
                existing_booking.booking_date
                <= booking.booking_date
                <= existing_booking.booked_until
                or existing_booking.booking_date
                <= booking.booked_until
                <= existing_booking.booked_until
            ):
                return True

        return False


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingData, user: User = Depends(get_authenticated_user)
):
    with session:
        try:
            booking = Booking(**(dict(vars(data).items())))
            booking.user_id = user.id

            stmt = select(FootballField).where(
                FootballField.id == data.field_id
            )
            field: FootballField = session.scalar(stmt)
            if not field:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Field not found",
                )

            if overlap(booking):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Bookng overlaps with another booking",
                )

            session.add(booking)
            session.commit()

            session.refresh(booking)
            return booking.json()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


@router.get(
    "/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)]
)
def get_bookings():
    with session:
        stmt = select(Booking)
        return [booking.json() for booking in session.scalars(stmt)]


@router.get("/user", status_code=status.HTTP_200_OK)
def get_user_bookings(user: User = Depends(get_authenticated_user)):
    with session:
        stmt = select(Booking).where(Booking.user_id == user.id)
        return [booking.json() for booking in session.scalars(stmt)]


@router.get(
    "/field/{field_id}/availability/{target_date}",
    status_code=status.HTTP_200_OK,
)
def get_field_availability(field_id: int, target_date: str):
    with session:
        stmt = select(FootballField).where(FootballField.id == field_id)
        field: FootballField = session.scalar(stmt)

        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found",
            )

        stmt = select(Booking).where(Booking.field_id == field_id)
        bookings: list[Booking] = session.scalars(stmt)

        return [
            {
                "from": booking.booking_date.time(),
                "to": booking.booked_until.time(),
            }
            for booking in bookings
            if booking.booking_date.date() == date.fromisoformat(target_date)
            and booking.status != BookingStatus.canceled
        ]


@router.get("/field/{field_id}", status_code=status.HTTP_200_OK)
def get_field_bookings(
    field_id: int, owner: Owner = Depends(get_authenticated_owner)
):
    with session:
        stmt = select(FootballField).where(FootballField.id == field_id)
        field: FootballField = session.scalar(stmt)

        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found",
            )

        if field.owner_id != owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to view this field",
            )

        stmt = select(Booking).where(Booking.field_id == field_id)
        bookings: list[Booking] = session.scalars(stmt)

        return [booking.json() for booking in bookings]


@router.get("/{booking_id}", status_code=status.HTTP_200_OK)
def get_booking(booking_id: int, user: User = Depends(get_authenticated_user)):
    with session:
        stmt = select(Booking).where(Booking.id == booking_id)
        booking: Booking = session.scalar(stmt)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        if is_admin(user):
            return booking.json()

        stmt = select(FootballField).where(
            FootballField.id == booking.field_id
        )
        field: FootballField = session.scalar(stmt)

        if isinstance(user, Owner) and field.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to view this booking",
            )

        if booking.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to view this booking",
            )

        return booking.json()


@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
def delete_booking(
    booking_id: int,
    user: User = Depends(get_authenticated_user),
):
    with session:
        stmt = select(Booking).where(Booking.id == booking_id)
        booking: Booking = session.scalar(stmt)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        stmt = select(FootballField).where(
            FootballField.id == booking.field_id
        )
        field: FootballField = session.scalar(stmt)

        if isinstance(user, Owner) and field.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this booking",
            )

        if booking.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this booking",
            )

        session.delete(booking)
        session.commit()

        return {"message": "Booking deleted successfully"}


@router.put("/{booking_id}", status_code=status.HTTP_200_OK)
def set_booking_status(
    booking_id: int,
    update: BookingUpdate,
    owner: Owner = Depends(get_authenticated_owner),
):
    with session:
        stmt = select(Booking).where(Booking.id == booking_id)
        booking: Booking = session.scalar(stmt)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        stmt = select(FootballField).where(
            FootballField.id == booking.field_id
        )
        field: FootballField = session.scalar(stmt)

        if field.owner_id != owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this booking",
            )

        booking.status = update.status
        session.add(booking)
        session.commit()
        session.refresh(booking)

        return booking.json()
