"""Подключение к базе.

TODO (M2): базовый класс моделей, создание движка и фабрики сессий.
"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """TODO: базовый класс ORM-моделей."""
    pass

def make_engine(database_url: str) -> Engine:
    """TODO: вернуть Engine по строке подключения."""
    return create_engine(database_url, echo=True, pool_size=5, max_overflow=10)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """TODO: вернуть фабрику сессий для движка."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)