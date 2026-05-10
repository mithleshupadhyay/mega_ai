from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from mega_ai.api import evals, jobs, prompts, query
from mega_ai.api.errors import http_exception_handler, validation_exception_handler
from mega_ai.db.pgv.crud.seeds import seed_static_data
from mega_ai.db.pgv.db import SessionLocal, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_static_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Mega AI Multi-Agent Assignment",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.include_router(query.router)
app.include_router(jobs.router)
app.include_router(evals.router)
app.include_router(prompts.router)
