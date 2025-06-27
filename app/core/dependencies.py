from typing import Annotated

from fastapi import Depends

from articles.services import ArticleService, FreeGPTSummaryService, IArticleService
from core.config import settings
from core.utils.unitofwork import IUnitOfWork, UnitOfWork
from core.utils.summary_abstract import AbstractSummaryService


async def get_uow():
    async with UnitOfWork() as uow:
        yield uow


def get_summary_service() -> AbstractSummaryService:
    provider = settings.summary.provider
    
    if provider == "free_gpt":
        return FreeGPTSummaryService()
    # В будущем можно добавить другие провайдеры:
    # elif provider == "openai":
    #     return OpenAISummaryService()
    # elif provider == "local":
    #     return LocalSummaryService()
    else:
        # Fallback к FreeGPT
        return FreeGPTSummaryService()


def get_article_service(
    summary_service: AbstractSummaryService = Depends(get_summary_service),
) -> IArticleService:
    return ArticleService(summary_service)


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]

ArticleServiceDep = Annotated[IArticleService, Depends(get_article_service)]
