from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class RunConfig(BaseModel):
    mode: Literal["DEBUG", "TEST", "PROD"] = "DEBUG"
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix_api: str = "/api"
    prefix_wiki: str = "/wiki"


class ApiTags(BaseModel):
    tag_article: str = "Articles"


class DatabaseConfig(BaseModel):
    prod_url: PostgresDsn
    debug_url: PostgresDsn
    test_url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class ParserConfig(BaseModel):
    wiki_base: str = "https://ru.wikipedia.org"
    base_death: int = 5
    death: int = 5
    timeout: int = 30  # Секунды


class SummaryConfig(BaseModel):
    provider: Literal["free_gpt", "openai", "deepseek"] = "free_gpt"
    max_text_length: int = 3000
    max_tokens: int = 200
    temperature: float = 0.3


class LoggerConfig(BaseModel):
    logger_name: str = "parser-app"
    log_info: Literal["INFO", "DEBUG", "WARNING", "CRITICAL"] = "INFO"


class Settings(BaseSettings):
    # Run
    run: RunConfig = RunConfig()

    # Api prefix
    api: ApiPrefix = ApiPrefix()

    # Tags
    tags: ApiTags = ApiTags()

    # Database
    db: DatabaseConfig

    # Host Data
    http_type: str
    hostname: str

    # Logging
    logger: LoggerConfig = LoggerConfig()

    # Parsing
    parser: ParserConfig = ParserConfig()
    
    # Summary
    summary: SummaryConfig = SummaryConfig()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    @staticmethod
    def get_database_url_by_mode():
        url = ""
        mode = settings.run.mode
        if mode == "TEST":
            url = str(settings.db.test_url)
        elif mode == "DEBUG":
            url = str(settings.db.debug_url)
        elif mode == "PROD":
            url = str(settings.db.prod_url)
        return url


settings = Settings()
