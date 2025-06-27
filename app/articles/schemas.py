from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, HttpUrl


class ArticleBaseSchema(BaseModel):
    title: str
    url: str
    content: Optional[str] = None


class ArticleCreateSchema(ArticleBaseSchema):
    parent_id: Optional[UUID4] = None


class ArticleResponse(ArticleBaseSchema):
    id: UUID4
    parent_id: Optional[UUID4] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleSummaryBaseSchema(BaseModel):
    summary: str


class ArticleSummaryCreateSchema(ArticleSummaryBaseSchema):
    article_id: UUID4


class ArticleSummaryResponse(ArticleSummaryBaseSchema):
    id: UUID4
    article_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class ParseWikiResponse(BaseModel):
    article_id: UUID4
    message: str = "Article parsed and summary generated successfully"


class GetSummaryResponse(BaseModel):
    article_id: UUID4
    title: str
    url: str
    summary: str
    created_at: datetime


class WikiArticleSchema(BaseModel):
    title: str
    url: str
    content: str
    children: List["WikiArticleSchema"]


class URLBodySchema(BaseModel):
    url: HttpUrl
