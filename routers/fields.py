from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, HTTPException
from db import session, FootballField
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/fields")


@dataclass
class FieldData:
    owner_id: int

    name: str
    location: str
    surface_type: Optional[str]

    width: float
    height: float

    start_time: datetime
    end_time: datetime


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_field(data: FieldData):
    with session:
        try:
            field = FootballField(**(dict(vars(data).items())))
            session.add(field)
            session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
