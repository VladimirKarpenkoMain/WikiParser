import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.mixins import CreatedAtMixin, UUIDIdIndexMixin
from core.models import Base


class Article(Base, UUIDIdIndexMixin, CreatedAtMixin):

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("articles.id"), nullable=True
    )

    # Relationships
    parent = relationship(
        "Article", remote_side="Article.id", back_populates="children"
    )
    children: Mapped[List["Article"]] = relationship("Article", back_populates="parent")
    summary = relationship("ArticleSummary", back_populates="article", uselist=False)


class ArticleSummary(Base, UUIDIdIndexMixin, CreatedAtMixin):
    __tablename__ = "article_summaries"

    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articles.id"), unique=True, nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="summary")
