"""HTTP-сервис мини-ассистента.

TODO (M0–M5): конфигурация, зависимости, lifespan (движок БД, эмбеддер,
LLM-клиент) и маршруты. Список маршрутов и их поведение — в SPEC.md.
"""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.config import Config, Settings
from app.db import repository
from app.db.base import make_engine, make_session_factory
from app.domain.chunking import chunk_text
from app.domain.embeddings import Embedder, create_embedder
from app.domain.llm_client import LLMClient
from app.domain.retrieval import top_k
from app.schemas import AskRequest, AskResponse, DocumentCreate, DocumentOut, ErrorResponse, HealthResponse, SourceOut


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config = Config(Settings())
    settings = config.get_settings()
    config.start_logging()
    embedder = create_embedder(settings)
    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)
    llm = LLMClient(base_url=settings.llm_base_url, model=settings.llm_model, api_key=settings.llm_api_key, timeout=settings.llm_timeout)
    app.state.settings = settings
    app.state.logger = config.get_logger()
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.embedder = embedder
    app.state.llm = llm
    app.state.logger.info("Application started.")
    yield
    app.state.logger.info("Application shutting down.")
    engine.dispose()

app = FastAPI(title="mini_assistant", version="1.0.0", lifespan = lifespan)

@app.get("/health", response_model = HealthResponse)
async def health() -> HealthResponse:
    app.state.logger.info("Health check requested.")
    return HealthResponse()

@app.post("/documents", response_model = DocumentOut, status_code = 201, responses = {422: {"model": ErrorResponse}})
async def create_document(document: DocumentCreate) -> DocumentOut:
    app.state.logger.info("Creating document.")
    chunks = chunk_text(document.text)
    if not chunks:
        app.state.logger.warning("Document text is empty or cannot be chunked.")
        raise HTTPException(status_code=422, detail="Document text is empty or cannot be chunked.")
    embeddings = app.state.embedder.embed(chunks)
    chunks_and_embeddings = list(zip(chunks, embeddings, strict=True))
    with app.state.session_factory() as conn:
        doc = repository.create_document(conn, document.title, chunks_and_embeddings)
        chunk_count = repository.count_chunks(conn, doc.id)
        app.state.logger.info(f"Document created with ID {doc.id} and {chunk_count} chunks.")
        return DocumentOut(id=doc.id, title=doc.title, created_at=doc.created_at, chunks=chunk_count)

@app.get("/documents/{id}", response_model = DocumentOut, responses = {404: {"model": ErrorResponse}})
async def get_document(id: int) -> DocumentOut:
    app.state.logger.info(f"Getting document with ID {id}.")
    with app.state.session_factory() as conn:
        doc = repository.get_document(conn, id)
        if doc is None:
            app.state.logger.warning(f"Document with ID {id} not found.")
            raise HTTPException(status_code=404, detail="Document not found.")
        chunk_count = repository.count_chunks(conn, doc.id)
        app.state.logger.info(f"Document with ID {id} retrieved with {chunk_count} chunks.")
        return DocumentOut(id = doc.id, title = doc.title, created_at = doc.created_at, chunks=chunk_count)

@app.get("/documents", response_model = list[DocumentOut])
async def list_documents() -> list[DocumentOut]:
    app.state.logger.info("Listing documents.")
    with app.state.session_factory() as conn:
        docs = repository.list_documents(conn)
        app.state.logger.info(f"{len(docs)} documents retrieved.")
        return [DocumentOut(id = doc.id, title = doc.title, created_at = doc.created_at, chunks=repository.count_chunks(conn, doc.id)) for doc in docs]

async def augmentation(question: str, embedder: Embedder, k: int | None) -> tuple[list[dict[str,str]], list[SourceOut]]:
    app.state.logger.info(f"Augmenting question: {question}")
    query_embedding = embedder.embed([question])[0]
    k = k if k is not None else app.state.settings.top_k
    with app.state.session_factory() as conn:
        chunks = repository.list_chunks(conn)
        items = [(chunk.id, chunk.embedding) for chunk in chunks]
        chunk_by_id = {chunk.id: chunk for chunk in chunks}
        selected = top_k(query = query_embedding, items = items, k = k)
        sources = []
        context_chunks = []
        for chunk_id, score in selected:
            chunk = chunk_by_id[chunk_id]
            context_chunks.append(f"Chunk {chunk.id} (Document {chunk.document_id}): {chunk.text}")
            sources.append(SourceOut(chunk_id = chunk.id, document_id = chunk.document_id, score = score, text = chunk.text))
        context = "\n\n".join(context_chunks)
        messages = [
            {
                "role": "system",
                "content": (
                    "Отвечай на вопрос только на основе контекста."
                    "Если ответа в контексте нет, скажи об этом."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Контекст:\n{context}\n\n"
                    f"Вопрос: {question}"
                ),
            },
        ]
    app.state.logger.info(f"Augmentation completed. {len(sources)} sources found.")
    return messages, sources

@app.post("/ask", response_model = AskResponse, responses = {503: {"model": ErrorResponse}})
async def ask(request: AskRequest) -> AskResponse:
    app.state.logger.info(f"Received question: {request.question}")
    messages, sources = await augmentation(request.question, app.state.embedder, request.k)
    try:
        answer = await app.state.llm.chat(messages)
    except httpx.HTTPError as e:
        app.state.logger.error(f"Error during LLM chat: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable.") from e
    app.state.logger.info(f"Answer generated: {answer}")
    return AskResponse(answer=answer, sources=sources)

async def generate_stream(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    try:
        async for delta in app.state.llm.stream(messages):
            event = {"token": delta}
            yield f"data: {json.dumps(event, ensure_ascii= False)}\n\n"
    except httpx.HTTPError as e:
        app.state.logger.error(f"Error during streaming: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable.") from e
    yield "data: [DONE]\n\n"
    app.state.logger.info("Stream completed.")

@app.post("/ask/stream", response_class = StreamingResponse, responses = {503: {"model": ErrorResponse}})
async def ask_stream(request: AskRequest) -> StreamingResponse:
    app.state.logger.info(f"Received streaming question: {request.question}")
    messages, _sources = await augmentation(request.question, app.state.embedder, request.k)
    app.state.logger.info("Starting streaming response.")
    return StreamingResponse(generate_stream(messages), media_type="text/event-stream")
    

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
