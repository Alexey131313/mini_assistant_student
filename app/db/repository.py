"""Операции с базой.

TODO (M2): сохранение документа с чанками и функции чтения.
Сигнатуры сохранить — на них опираются тесты.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Chunk, Document


def create_document(session: Session, title: str, chunks: list[tuple[str, list[float]]]) -> Document:
    """TODO: сохранить документ и его чанки одной транзакцией."""
    doc = Document(title=title)
    session.add(doc)
    session.flush()
    for pos, (text, embedding) in enumerate(chunks):
        chunk = Chunk(document_id = doc.id, position = pos, text = text, embedding = embedding)
        session.add(chunk)
    session.commit()
    return doc


def list_documents(session: Session) -> list[Document]:
    """TODO: вернуть документы (новые сверху)."""
    stmt = select(Document).order_by(Document.created_at.desc())
    return list(session.scalars(stmt).all())


def get_document(session: Session, document_id: int) -> Document | None:
    """TODO: вернуть документ по id или None."""
    stmt =select(Document).where(Document.id == document_id)
    return session.scalars(stmt).first()


def count_chunks(session: Session, document_id: int) -> int:
    """TODO: число чанков у документа."""
    stmt = select(func.count()).select_from(Chunk).where(Chunk.document_id == document_id)
    return session.scalar(stmt) or 0


def list_chunks(session: Session) -> list[Chunk]:
    """TODO: все чанки (для поиска)."""
    stmt = select(Chunk)
    return list(session.scalars(stmt).all())
