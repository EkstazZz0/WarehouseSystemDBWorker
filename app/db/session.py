from sqlmodel import Session, create_engine
from contextlib import contextmanager

from core.config import db_connect_configuration

engine=create_engine(**db_connect_configuration)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
