import os
from sqlmodel import SQLModel, create_engine, Session
from .models import *  # noqa

database_url = os.environ.get("POSTGRESQL_URL")
engine = create_engine(database_url)


SQLModel.metadata.create_all(bind=engine)
session = Session(autocommit=False, autoflush=False, bind=engine)
