from typing import Optional

import bcrypt
from sqlmodel import Field, SQLModel


class Owner(SQLModel, table=True):
    __tablename__ = "owners"

    id: int = Field(primary_key=True)

    username: str = Field(unique=True, nullable=False)
    name: str
    password: str

    email: Optional[str]
    phone_number: Optional[str]
    instagram: Optional[str]

    def verify_password(self, password: str) -> bool:
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash

    def json(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "contacts": {
                "email": self.email,
                "phone_number": self.phone_number,
                "instagram": self.instagram,
            },
        }
