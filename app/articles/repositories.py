from articles.models import Article, ArticleSummary
from core.utils.repository import SQLAlchemyRepository


class ArticleRepository(SQLAlchemyRepository):
    model = Article


class ArticleSummaryRepository(SQLAlchemyRepository):
    model = ArticleSummary
