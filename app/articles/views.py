import logging

from fastapi import APIRouter

from articles.schemas import GetSummaryResponse, ParseWikiResponse, URLBodySchema
from core.config import settings
from core.dependencies import ArticleServiceDep, UOWDep

logger = logging.getLogger(settings.logger.logger_name)

router = APIRouter(prefix=settings.api.prefix_api, tags=[settings.tags.tag_article])


@router.post("/wiki/parse", response_model=ParseWikiResponse)
async def parse_wiki_endpoint(
    body_url: URLBodySchema,
    uow: UOWDep,
    article_service: ArticleServiceDep,
):
    """
    Эндпоинт для парсинга Wikipedia статьи и генерации summary
    """
    logger.info(
        "Received parsing request for article: %s, depth: %s",
        body_url.url,
        settings.parser.death,
    )
    article_id = await article_service.parse_and_save_wiki_article(
        url=str(body_url.url),
        uow=uow,
        depth=settings.parser.death,
    )
    logger.info(f"Article successfully processed, ID: %s", article_id)
    return ParseWikiResponse(article_id=article_id)


@router.post("/wiki/summary", response_model=GetSummaryResponse)
async def get_article_summary_endpoint(
    body_url: URLBodySchema,
    uow: UOWDep,
    article_service: ArticleServiceDep,
):
    """
    Эндпоинт для получения summary статьи по URL
    """
    logger.info("Received summary request for article: %s", body_url.url)
    result = await article_service.get_article_summary_by_url(
        url=str(body_url.url),
        uow=uow,
    )
    return GetSummaryResponse(**result)
