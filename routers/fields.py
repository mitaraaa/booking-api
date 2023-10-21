from datetime import time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from db import FootballField, Owner, session
from routers.auth import get_authenticated_owner

router = APIRouter(prefix="/fields")


class FieldData(BaseModel):
    owner_id: int | None

    name: str | None
    location: str | None
    surface_type: str | None

    width: float | None
    length: float | None

    start_time: time | None
    end_time: time | None

    def __init__(self, **data):
        for key, value in data.items():
            if key in ["start_time", "end_time"] and isinstance(value, str):
                data[key] = time.fromisoformat(value)

        super().__init__(**data)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_field(
    data: FieldData, owner: Owner = Depends(get_authenticated_owner)
):
    with session:
        try:
            field = FootballField(**(dict(vars(data).items())))
            field.owner_id = owner.id

            session.add(field)
            session.commit()

            return {"message": "Field created successfully"}
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


@router.get("/owner", status_code=status.HTTP_200_OK)
def get_owner_fields(owner: Owner = Depends(get_authenticated_owner)):
    with session:
        stmt = select(FootballField).where(FootballField.owner_id == owner.id)
        return [x.json() for x in session.scalars(stmt)]


@router.put(
    "/{field_id}",
    status_code=status.HTTP_200_OK,
)
def update_field(
    field_id: int,
    data: FieldData,
    owner: Owner = Depends(get_authenticated_owner),
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
                detail="You are not the owner of this field",
            )

        for key, value in dict(vars(data).items()).items():
            if value:
                setattr(field, key, value)

        session.add(field)
        session.commit()

        return {"message": "Field updated successfully"}


@router.get("/{field_id}", status_code=status.HTTP_200_OK)
def get_field(field_id: int):
    with session:
        stmt = select(FootballField).where(FootballField.id == field_id)
        field = session.scalar(stmt)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found",
            )
        return field.json()


@router.delete(
    "/{field_id}",
    status_code=status.HTTP_200_OK,
)
def delete_field(
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
                detail="You are not the owner of this field",
            )

        session.delete(field)
        session.commit()

        return {"message": "Field deleted successfully"}


@router.get("/", status_code=status.HTTP_200_OK)
def get_fields():
    with session:
        stmt = select(FootballField)
        return [x.json() for x in session.scalars(stmt)]
