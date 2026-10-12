"""HTTP-сервис мини-ассистента.

TODO (M0–M5): конфигурация, зависимости, lifespan (движок БД, эмбеддер,
LLM-клиент) и маршруты. Список маршрутов и их поведение — в SPEC.md.
"""

from fastapi import FastAPI
#from fastapi.responses import Response
from app.schemas import HealthResponse, DocumentCreate, DocumentOut, AskRequest, AskResponse, ErrorResponse

app = FastAPI(title="mini_assistant", version="1.0.0")

@app.get("/health", response_model = HealthResponse, responses = {400: {"model": ErrorResponse}})
async def health() -> HealthResponse:
    return HealthResponse()

@app.post("/documents", response_model = DocumentCreate, responses = {400: {"model": ErrorResponse}})
async def create_document(document: DocumentCreate) -> DocumentOut:
    # Здесь будет реализация создания документа
    pass

@app.get("/documents/{document_id}", response_model = DocumentOut, responses = {400: {"model": ErrorResponse}})
async def get_document(document_id: int) -> DocumentOut:
    # Здесь будет реализация получения документа по ID
    pass

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
