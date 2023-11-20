from datetime import time
from typing import Optional

from sqlmodel import Field, SQLModel

Meters = float


class FootballField(SQLModel, table=True):
    __tablename__ = "football_fields"

    id: int = Field(primary_key=True)
    owner_id: int

    name: str
    location: str
    surface_type: Optional[str]

    about: Optional[str]
    image: Optional[str]

    width: Meters
    length: Meters

    price: float

    start_time: time
    end_time: time

    def json(self) -> dict:
        return dict(vars(self).items())
