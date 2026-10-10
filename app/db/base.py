"""Подключение к базе.

TODO (M2): базовый класс моделей, создание движка и фабрики сессий.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """TODO: базовый класс ORM-моделей."""


def make_engine(database_url: str):
    """TODO: вернуть Engine по строке подключения."""
    raise NotImplementedError


def make_session_factory(engine):
    """TODO: вернуть фабрику сессий для движка."""
    raise NotImplementedError
