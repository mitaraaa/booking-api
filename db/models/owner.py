from typing import Optional

from db.models.user import User


class Owner(User, table=True):
    __tablename__ = "owners"

    email: Optional[str]
    phone_number: Optional[str]
    instagram: Optional[str]

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
