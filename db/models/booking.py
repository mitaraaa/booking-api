from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: int = Field(primary_key=True)

    user_id: int
    field_id: int

    booking_date: datetime
    booked_until: datetime

    status: BookingStatus = Field(default=BookingStatus.pending.value)
