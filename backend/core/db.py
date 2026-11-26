from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine

from core.config import DATABASE_URL

metadata = MetaData()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@contextmanager
def transaction():
    with engine.begin() as conn:
        yield conn
