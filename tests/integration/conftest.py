"""Фикстуры интеграционных тестов: реальная база из TEST_DATABASE_URL."""

import os

import pytest
from sqlalchemy.orm import Session

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def db_engine():
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL не задан")
    from app.db import models  # noqa: F401
    from app.db.base import Base, make_engine

    engine = make_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def session(db_engine) -> Session:
    from app.db.base import make_session_factory
    from app.db.models import Chunk, Document

    factory = make_session_factory(db_engine)
    with factory() as active_session:
        active_session.query(Chunk).delete()
        active_session.query(Document).delete()
        active_session.commit()
        yield active_session


@pytest.fixture()
def client(db_engine):
    from fastapi.testclient import TestClient

    from app.db.base import make_session_factory
    from app.db.models import Chunk, Document
    from app.main import app

    factory = make_session_factory(db_engine)
    with factory() as active_session:
        active_session.query(Chunk).delete()
        active_session.query(Document).delete()
        active_session.commit()

    with TestClient(app) as test_client:
        yield test_client
