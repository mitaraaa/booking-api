import bcrypt
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)

    username: str = Field(unique=True, nullable=False)
    name: str
    password: str

    def verify_password(self, password: str) -> bool:
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash
