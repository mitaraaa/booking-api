from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import Booking, FootballField, User, session
from db.models.booking import BookingStatus
from routers.auth import get_admin_user, get_authenticated_user

router = APIRouter(prefix="/bookings")


class BookingData(BaseModel):
    user_id: int | None
    field_id: int | None

    booking_date: datetime | None
    booked_until: datetime | None

    status: BookingStatus | None = BookingStatus.pending


class BookingTime(BaseModel):
    booking_date: datetime | None
    booked_until: datetime | None

    def __str__(self) -> str:
        return f"{self.booking_date} - {self.booked_until}"


class TargetDate(BaseModel):
    target_date: date


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingData, user: User = Depends(get_authenticated_user)
):
    with session:
        try:
            booking = Booking(**(dict(vars(data).items())))
            booking.user_id = user.id

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


@router.get("/field/{field_id}", status_code=status.HTTP_200_OK)
def get_field_bookings(field_id: int):
    with session:
        stmt = select(Booking).where(Booking.field_id == field_id)

        bookings = []
        for booking in session.scalars(stmt):
            booking: dict = booking.json()
            booking.pop("user_id")
            bookings.append(booking)

        return bookings


@router.get("field/{field_id}/availability", status_code=status.HTTP_200_OK)
def get_field_availability(field_id: int, target_date: TargetDate):
    with session:
        stmt = select(FootballField).where(FootballField.id == field_id)
        field: FootballField = session.scalar(stmt)

        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found",
            )

        stmt = select(Booking).where(Booking.field_id == field_id)

        bookings = []
        for index, booking in enumerate(session.scalars(stmt)):
            booking: dict = booking.json()
            if booking["booking_date"].date() != target_date.target_date:
                continue

            if index == 0:
                bookings.append(
                    BookingTime(
                        datetime.combine(
                            target_date.target_date, field.start_time
                        ),
                        booking["booking_date"],
                    )
                )
                continue

            bookings.append(
                BookingTime(bookings[-1].booked_until, booking["booking_date"])
            )

        return bookings


@router.get("/{booking_id}", status_code=status.HTTP_200_OK)
def get_booking(booking_id: int):
    with session:
        stmt = select(Booking).where(Booking.id == booking_id)
        booking: Booking = session.scalar(stmt)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        return booking.json()


@router.put("/{booking_id}", status_code=status.HTTP_200_OK)
def update_booking(
    booking_id: int,
    data: BookingData,
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

        if booking.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this booking",
            )

        booking.booking_date = data.booking_date
        booking.booked_until = data.booked_until
        booking.status = data.status

        session.add(booking)
        session.commit()

        session.refresh(booking)
        return {
            "message": "Booking updated successfully",
            "booking": booking.json(),
        }


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

        if booking.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this booking",
            )

        session.delete(booking)
        session.commit()

        return {"message": "Booking deleted successfully"}
