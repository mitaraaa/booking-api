from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, HTTPException
from db import session, Booking
from sqlalchemy.exc import IntegrityError

from db.models.booking import BookingStatus


router = APIRouter(prefix="/bookings")


@dataclass
class BookingData:
    user_id: int
    field_id: int

    booking_date: datetime
    booked_until: datetime

    status: Optional[BookingStatus] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingData):
    with session:
        try:
            booking = Booking(**(dict(vars(data).items())))
            session.add(booking)
            session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
