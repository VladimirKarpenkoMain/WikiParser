from abc import ABC, abstractmethod
from typing import List, Optional, Sequence, Type, TypeVar

from sqlalchemy import Result, insert, select, update
from sqlalchemy.dialects.postgresql import insert as psql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.base import ObjectNotFound
from core.models import Base

T = TypeVar("T", bound=Base)


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def get(self, model_id: int):
        raise NotImplementedError

    @abstractmethod
    async def list(
        self, filter_by: Optional[dict] = None, order_by: Optional[List] = None
    ):
        raise NotImplementedError

    @abstractmethod
    async def update(self, model_id: int, data: dict, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, model_id: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model: T = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: dict) -> Type[T]:
        stmt = insert(self.model).values(**data).returning(self.model)
        result: Result = await self.session.execute(stmt)
        model = result.scalar_one()
        return model

    async def add_or_get(
        self,
        data: dict,
        *,
        conflict_cols: Optional[Sequence[str]] = None,
    ) -> Type[T]:
        if not conflict_cols:
            conflict_cols = [
                col.name for col in self.model.__table__.primary_key.columns
            ]

        stmt = (
            psql_insert(self.model)
            .values(**data)
            .on_conflict_do_nothing(index_elements=list(conflict_cols))
            .returning(self.model)
        )
        result: Result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()

        if instance:
            return instance

        filter_kwargs = {c: data[c] for c in conflict_cols if c in data}
        return await self.get(**filter_kwargs)

    async def add_many(self, data: list) -> Sequence[Type[T]]:
        stmt = insert(self.model).values(data).returning(self.model)
        result: Result = await self.session.execute(stmt)
        models = result.scalars().all()
        return models

    async def get(self, model_id: Optional[int] = None, **kwargs) -> Type[T]:
        stmt = select(self.model)
        if model_id:
            stmt = stmt.where(self.model.id == model_id)
        stmt = stmt.filter_by(**kwargs)
        result: Result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return model

    async def get_or_404(self, model_id: Optional[int] = None, **kwargs) -> Type[T]:
        model = await self.get(model_id=model_id, **kwargs)
        if model is not None:
            return model
        raise ObjectNotFound(object_name=self.model.__name__, obj_id=model_id)

    async def list(
        self,
        filter_by: Optional[dict] = None,
        order_by: Optional[List] = None,
    ) -> List[Type[T]]:
        stmt = select(self.model)
        if filter_by:
            stmt = stmt.filter_by(**filter_by)
        if order_by:
            stmt = stmt.order_by(*order_by)
        result: Result = await self.session.execute(stmt)
        objects = result.scalars().all()
        return list(objects)

    async def update(
        self,
        model_id: int,
        update_values: dict,
        **kwargs,
    ) -> Optional[Type[T]]:
        stmt = update(self.model).where(self.model.id == model_id)
        if kwargs:
            stmt = stmt.filter_by(**kwargs)
        stmt = stmt.values(**update_values).returning(self.model)

        result: Result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model

    async def delete(self, instance: Type[T]):
        await self.session.delete(instance)
