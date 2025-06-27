import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from articles.views import router as articles_router
from core.config import settings
from core.db import db_helper
from core.utils.error_handlers import register_errors_handlers
from core.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    setup_logger()
    logger = logging.getLogger(settings.logger.logger_name)
    logger.info("Application starting")
    yield
    # shutdown
    logger.info("Application shutting down")
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
    title="Wiki Article Parser",
    description="API для парсинга статей Wikipedia и генерации summary",
    version="1.0.0",
)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(articles_router)

register_errors_handlers(app=main_app)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
