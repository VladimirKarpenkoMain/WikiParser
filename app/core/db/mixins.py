import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

UUID_ID = uuid.UUID


class IntIdMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class IntIdIndexMixin:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class UUIDIdMixin:
    id: Mapped[UUID_ID] = mapped_column(primary_key=True, default=uuid.uuid4)


class UUIDIdIndexMixin:
    id: Mapped[UUID_ID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
