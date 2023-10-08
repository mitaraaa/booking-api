import bcrypt
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)

    username: str = Field(unique=True, nullable=False)
    name: str
    password: str

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password.encode())

    def json(self) -> dict:
        return self.__repr__()

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
        }
