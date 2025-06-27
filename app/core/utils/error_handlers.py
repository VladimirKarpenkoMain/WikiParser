import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import DatabaseError

from core.config import settings

logger = logging.getLogger(settings.logger.logger_name)


def register_errors_handlers(app: FastAPI) -> None:
    @app.exception_handler(DatabaseError)
    def handle_db_error(request: Request, exc: DatabaseError):
        logger.error(
            "Database Error: %s",
            exc,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal Server Error"},
        )
