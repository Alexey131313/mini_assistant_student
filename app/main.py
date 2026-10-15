"""HTTP-сервис мини-ассистента.

TODO (M0–M5): конфигурация, зависимости, lifespan (движок БД, эмбеддер,
LLM-клиент) и маршруты. Список маршрутов и их поведение — в SPEC.md.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schemas import HealthResponse, DocumentCreate, DocumentOut, AskRequest, AskResponse, ErrorResponse
from app.config import Settings
from app.db.base import create_engine, make_session_factory
from app.domain.embeddings import create_embedder

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = await Settings()
    engine = await create_engine(settings.database_url)
    session_factory = await make_session_factory(engine)
    embedder = await create_embedder(settings.embedder_model, settings.embedder_dim)
    yield

app = FastAPI(title="mini_assistant", version="1.0.0", lifespan = lifespan)

@app.get("/health", response_model = HealthResponse, responses = {400: {"model": ErrorResponse}})
async def health() -> HealthResponse:
    return HealthResponse()

@app.post("/documents", response_model = DocumentCreate, responses = {400: {"model": ErrorResponse}})
async def create_document(document: DocumentCreate) -> DocumentOut:
    # Здесь будет реализация создания документа
    pass

@app.get("/documents/{id}", response_model = DocumentOut, responses = {400: {"model": ErrorResponse}})
async def get_document(id: int) -> DocumentOut:
    # Здесь будет реализация получения документа по ID
    pass

@app.get("/documents", response_model = list[DocumentOut], responses = {400: {"model": ErrorResponse}})
async def list_documents() -> list[DocumentOut]:
    # Здесь будет реализация получения списка документов
    pass

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
