import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

from .models import *  # noqa

load_dotenv()

database_url = os.environ.get("POSTGRESQL_URL")
engine = create_engine(database_url)


SQLModel.metadata.create_all(bind=engine)
session = Session(autocommit=False, autoflush=False, bind=engine)
