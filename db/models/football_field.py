from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class FootballField(SQLModel, table=True):
    __tablename__ = "football_fields"

    id: int = Field(primary_key=True)
    owner_id: int

    name: str
    location: str
    surface_type: Optional[str]

    width: float
    height: float

    start_time: datetime
    end_time: datetime
