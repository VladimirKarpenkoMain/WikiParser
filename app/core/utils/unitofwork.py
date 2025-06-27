import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import Result, Select

from articles.repositories import ArticleRepository, ArticleSummaryRepository
from core.config import settings
from core.db.db_helper import db_helper

logger = logging.getLogger(settings.logger.logger_name)


class IUnitOfWork(ABC):
    articles: ArticleRepository
    article_summaries: ArticleSummaryRepository

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    async def flush(self): ...

    @abstractmethod
    async def query(self, stmt: Select) -> Result: ...


class UnitOfWork:
    def __init__(self):
        self.session_factory = db_helper.session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.articles = ArticleRepository(self.session)
        self.article_summaries = ArticleSummaryRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type and not issubclass(exc_type, HTTPException):
            await self.session.rollback()
            logger.error("Unexpected error in UoW: %s - %s", exc_type, exc_val)

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def query(self, stmt: Select) -> Result:
        return await self.session.execute(stmt)

    async def flush(self):
        await self.session.flush()
