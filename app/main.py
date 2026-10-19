"""HTTP-сервис мини-ассистента.

TODO (M0–M5): конфигурация, зависимости, lifespan (движок БД, эмбеддер,
LLM-клиент) и маршруты. Список маршрутов и их поведение — в SPEC.md.
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.db import repository
from app.schemas import HealthResponse, DocumentCreate, DocumentOut, AskRequest, AskResponse, ErrorResponse
from app.config import Settings, Config
from app.db.base import make_engine, make_session_factory
from app.domain.embeddings import create_embedder
from app.domain.chunking import chunk_text
from app.domain.llm_client import LLMClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config(Settings())
    settings = config._settings
    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)
    embedder = create_embedder(settings)
    llm = LLMClient(settings)

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.embedder = embedder
    app.state.llm = llm
    yield

    engine.dispose()

app = FastAPI(title="mini_assistant", version="1.0.0", lifespan = lifespan)

@app.get("/health", response_model = HealthResponse, responses = {400: {"model": ErrorResponse}})
async def health() -> HealthResponse:
    return HealthResponse()

@app.post("/documents", response_model = DocumentOut, status_code = 201, responses = {400: {"model": ErrorResponse}})
async def create_document(document: DocumentCreate) -> DocumentOut:
    chunks = chunk_text(document.text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Document text is empty or cannot be chunked.")
    embedder = app.state.embedder
    embeddings = embedder.embed(chunks)
    chunks_and_embeddings = list(zip(chunks, embeddings, strict=True))
    with app.state.session_factory() as conn:
        doc = repository.create_document(conn, document.title, chunks_and_embeddings)
        chunk_count = repository.count_chunks(conn, doc.id)
        return DocumentOut(id=doc.id, title=doc.title, created_at=doc.created_at, chunks=chunk_count)

@app.get("/documents/{id}", response_model = DocumentOut, responses = {400: {"model": ErrorResponse}})
async def get_document(id: int) -> DocumentOut:
    with app.state.session_factory() as conn:
        doc = repository.get_document(conn, id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        chunk_count = repository.count_chunks(conn, doc.id)
        return DocumentOut(id = doc.id, title = doc.title, created_at = doc.created_at, chunks=chunk_count)

@app.get("/documents", response_model = list[DocumentOut], responses = {400: {"model": ErrorResponse}})
async def list_documents() -> list[DocumentOut]:
    with app.state.session_factory() as conn:
        docs = repository.list_documents(conn)
        return [DocumentOut(id = doc.id, title = doc.title, created_at = doc.created_at, chunks=repository.count_chunks(conn, doc.id)) for doc in docs]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
