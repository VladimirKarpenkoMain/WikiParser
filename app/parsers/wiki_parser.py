import logging
from typing import Optional, Set
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from articles.schemas import WikiArticleSchema
from core.config import settings

logger = logging.getLogger(settings.logger.logger_name)


async def parse_wikipedia_article(
    url: str,
    depth: int,
    client: Optional[httpx.AsyncClient] = None,
    visited: Optional[Set[str]] = None,
    base_url: str = settings.parser.wiki_base,
    timeout: int = settings.parser.timeout,
) -> Optional[WikiArticleSchema]:
    """
    Рекурсивно парсит статью Wikipedia и её связанные статьи
    """

    if depth == 0:
        logger.debug("Maximum depth reached for %r", url)
        return None

    if visited is None:
        visited = set()

    if url in visited:
        logger.debug("Article already visited: %s", url)
        return None

    visited.add(url)
    close_client = False

    if client is None:
        logger.debug("Creating new HTTP client")
        client = httpx.AsyncClient()
        close_client = True

    try:
        logger.debug("Request to %r", url)
        resp = await client.get(url, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Извлекаем заголовок
        title_tag = soup.find("h1", id="firstHeading")
        title = title_tag.text.strip() if title_tag else url
        logger.debug("Extracted title: %s", title)

        # Извлекаем контент
        content_div = soup.find("div", {"id": "mw-content-text"})
        content = ""
        if content_div:
            paragraphs = content_div.find_all("p")
            content = "\n".join(
                p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
            )
            logger.debug("Extracted content")

        # Ищем ссылки на другие статьи
        children = []
        if content_div:
            links = content_div.find_all("a", href=True)
            logger.debug("Found %s links in article", len(links))
            for link in links:
                if len(children) >= 5:
                    logger.debug("Maximum number of child articles reached")
                    break

                href = link.get("href", "")
                if (
                    isinstance(href, str)
                    and href.startswith("/wiki/")
                    and not any(x in href for x in [":", "#"])
                ):
                    child_url = urljoin(base_url, href)
                    if child_url in visited:
                        continue
                    logger.debug("Processing child link: %s", child_url)
                    child_article = await parse_wikipedia_article(
                        child_url, depth - 1, client, visited
                    )
                    if child_article:
                        children.append(child_article)
                        logger.debug("Added child article: %s", child_article.title)
        logger.info(
            "Successfully parsed article: %s with %s child articles",
            title,
            len(children),
        )
        return WikiArticleSchema(
            title=title, url=url, content=content, children=children
        )

    except Exception as e:
        logger.error(f"Error parsing %s: %s", url, e, exc_info=True)
        return None

    finally:
        if close_client:
            logger.debug("Closing HTTP client")
            await client.aclose()
