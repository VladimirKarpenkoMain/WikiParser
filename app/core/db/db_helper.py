from typing import Any, AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from core.config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        **params: Any,
    ) -> None:
        if params.get("poolclass") is NullPool:
            engine_params = {}
        else:
            engine_params = {
                "pool_size": pool_size,
                "max_overflow": max_overflow,
            }
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            **engine_params,
            **params,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


DATABASE_PARAMS: dict = {}
if settings.run.mode == "TEST":
    DATABASE_PARAMS["poolclass"] = NullPool

db_helper = DatabaseHelper(
    url=settings.get_database_url_by_mode(),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    **DATABASE_PARAMS,
)
