"""Операции с базой.

TODO (M2): сохранение документа с чанками и функции чтения.
Сигнатуры сохранить — на них опираются тесты.
"""

from sqlalchemy.orm import Session

from .models import Chunk, Document


def create_document(session: Session, title: str, chunks: list[tuple[str, list[float]]]) -> Document:
    """TODO: сохранить документ и его чанки одной транзакцией."""
    raise NotImplementedError


def list_documents(session: Session) -> list[Document]:
    """TODO: вернуть документы (новые сверху)."""
    raise NotImplementedError


def get_document(session: Session, document_id: int) -> Document | None:
    """TODO: вернуть документ по id или None."""
    raise NotImplementedError


def count_chunks(session: Session, document_id: int) -> int:
    """TODO: число чанков у документа."""
    raise NotImplementedError


def list_chunks(session: Session) -> list[Chunk]:
    """TODO: все чанки (для поиска)."""
    raise NotImplementedError
