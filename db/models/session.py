from sqlmodel import Field, SQLModel


class UserSession(SQLModel, table=True):
    __tablename__ = "sessions"

    id: int = Field(primary_key=True)

    session_id: str = Field(nullable=False)
    user_id: int = Field(nullable=False)
    is_owner: bool = Field(nullable=False, default=False)
