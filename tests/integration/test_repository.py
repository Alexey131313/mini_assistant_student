"""Тесты операций с базой."""

import pytest

from app.db import repository

pytestmark = pytest.mark.integration


def test_create_and_read(session):
    document = repository.create_document(
        session,
        "Инструкция",
        [("первый кусок", [0.1, 0.2]), ("второй кусок", [0.3, 0.4])],
    )
    assert document.id is not None
    assert repository.count_chunks(session, document.id) == 2

    loaded = repository.get_document(session, document.id)
    assert loaded is not None
    assert loaded.title == "Инструкция"

    assert len(repository.list_chunks(session)) == 2
    assert [item.title for item in repository.list_documents(session)] == ["Инструкция"]


def test_get_missing_document(session):
    assert repository.get_document(session, 99999) is None
