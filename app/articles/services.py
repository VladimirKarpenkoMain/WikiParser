import logging
from abc import ABC, abstractmethod
from typing import Optional

from g4f.client import AsyncClient
from pydantic import UUID4

import core.exceptions.articles as article_exceptions
from articles.schemas import (ArticleCreateSchema, ArticleSummaryCreateSchema,
                                  WikiArticleSchema)
from core.config import settings
from core.utils.summary_abstract import AbstractSummaryService
from core.utils.unitofwork import IUnitOfWork
from parsers.wiki_parser import parse_wikipedia_article

logger = logging.getLogger(settings.logger.logger_name)


class IArticleService(ABC):
    """ Интерфейс для сервиса работы со статьями """
    
    @abstractmethod
    async def parse_and_save_wiki_article(
        self,
        url: str,
        uow: IUnitOfWork,
        depth: int,
    ) -> str:
        ...
    
    @abstractmethod
    async def get_article_summary_by_url(self, url: str, uow: IUnitOfWork):
        ...


class ArticleService(IArticleService):
    """ Сервис для работы со статьями """

    def __init__(self, summary_service: AbstractSummaryService):
        self.summary_service = summary_service

    async def _save_article_tree(
        self,
        article: WikiArticleSchema,
        uow: IUnitOfWork,
        parent_id: Optional[UUID4] = None,
    ):
        """ Рекурсивно сохраняет дерево статей в БД """
        logger.info("Saving article: %s", article.title)

        article_data = ArticleCreateSchema(
            title=article.title,
            url=article.url,
            content=article.content,
            parent_id=parent_id,
        )
        db_article = await uow.articles.add_or_get(
            article_data.model_dump(),
            conflict_cols=["url"],
        )
        await uow.flush()
        logger.debug("Article saved to DB with ID: %s", db_article.id)

        # Сохраняем вложенные статьи
        if article.children:
            logger.debug("Saving %r child articles", len(article.children))
            for child in article.children:
                await self._save_article_tree(child, uow, db_article.id)

        return db_article

    async def parse_and_save_wiki_article(
        self, url: str, uow: IUnitOfWork, depth: int = settings.parser.base_death
    ) -> str:
        """ Парсит статью Википедии и сохраняет в БД """
        logger.info("Starting parsing and saving article: %s, depth: %s", url, depth)

        # Парсим статью
        parsed_article = await parse_wikipedia_article(url=url, depth=depth)
        if not parsed_article:
            logger.error("Failed to parse article: %s", url)
            raise article_exceptions.FailedParsingException(url=url)

        logger.info("Article successfully parsed: %s", parsed_article.title)

        db_article = await self._save_article_tree(parsed_article, uow)
        logger.info("Article tree saved to DB, root article ID: %s", db_article.id)

        # Генерируем summary только для исходной статьи
        logger.info("Generating summary for root article")
        summary_text = await self.summary_service.generate_summary(
            text=parsed_article.content
        )

        summary_data = ArticleSummaryCreateSchema(
            article_id=db_article.id, summary=summary_text
        )
        await uow.article_summaries.add(summary_data.model_dump())
        await uow.commit()
        logger.info("Summary saved to DB for article ID: %s", db_article.id)

        return str(db_article.id)

    async def get_article_summary_by_url(self, url: str, uow: IUnitOfWork):
        """ Получает summary статьи по URL """
        logger.info("Getting article summary by URL: %s", url)

        article = await uow.articles.get(url=url)
        if not article:
            logger.warning("Article with URL %r not found in database", url)
            raise article_exceptions.ArticleNotFoundException(url=url)

        logger.debug("Found article: %s (ID: %s)", article.title, article.id)

        summary = await uow.article_summaries.get(article_id=article.id)
        if not summary:
            logger.warning("Summary for article %r not found", url)
            raise article_exceptions.SummaryNotFoundException(url=url)

        logger.info("Summary successfully retrieved for article: %s", article.title)
        return {
            "article_id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": summary.summary,
            "created_at": summary.created_at,
        }


class FreeGPTSummaryService(AbstractSummaryService):
    """ Сервис для генерации summary """

    async def generate_summary(self, text: str) -> str:
        """ Генерирует краткое содержание текста """
        logger.info("Starting summary generation")
        try:
            client = AsyncClient()
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Составь краткое содержание (summary) следующего текста "
                                   "на русском языке в 2–3 предложения. "
                                   "В ответе выведи только само summary — без заголовков, без слова «Summary», "
                                   "без каких-либо пояснений или дополнительных фраз.",
                    },
                    {"role": "user", "content": text[:settings.summary.max_text_length]},
                ],
                web_search=False,
            )
            summary = response.choices[0].message.content
            logger.info(
                "Summary successfully generated, length: %s characters", len(summary)
            )
            return summary
        except Exception as e:
            logger.error("Error generating summary: %s", e, exc_info=True)
            raise article_exceptions.FailedGeneratingSummaryException()
