from db.models.person import Person


class User(Person, table=True):
    __tablename__ = "users"
