"""Подключение к базе.

TODO (M2): базовый класс моделей, создание движка и фабрики сессий.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """TODO: базовый класс ORM-моделей."""
    pass

def make_engine(database_url: str):
    """TODO: вернуть Engine по строке подключения."""
    return create_engine(database_url, echo=True, pool_size=5, max_overflow=10)


def make_session_factory(engine):
    """TODO: вернуть фабрику сессий для движка."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)