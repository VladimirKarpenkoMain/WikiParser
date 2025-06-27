# Wiki Article Parser

Асинхронное веб-приложение для парсинга статей Wikipedia с рекурсивным обходом связанных статей и генерацией AI-суммаризации контента.

## Возможности

- **Рекурсивный парсинг** статей Wikipedia с настраиваемой глубиной вложенности
- **AI-суммаризация** контента с использованием различных провайдеров
- **Асинхронная обработка** для высокой производительности
- **Сохранение результатов** в PostgreSQL с полной структурой связей между статьями
- **RESTful API** для интеграции с внешними системами
- **Docker контейнеризация** для простого развертывания


## Технологии

- **Python 3.11+** - основной язык разработки
- **FastAPI** - веб-фреймворк для API
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
- **Pydantic** - валидация данных и сериализация
- **Alembic** - управление миграциями БД
- **PostgreSQL** - основная база данных
- **asyncpg** - асинхронный драйвер PostgreSQL
- **BeautifulSoup4** - парсинг HTML
- **httpx** - асинхронные HTTP запросы
- **g4f** - интеграция с AI провайдерами
- **lxml** - быстрый XML/HTML парсер


## Запуск через Docker Compose

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd WikiParser
```

2. **Создайте файл конфигурации:**
```bash
cp .env.docker.template .env.docker
# Отредактируйте .env.docker при необходимости
```

3. **Запустите приложение:**
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: **http://localhost:8000**


## API Документация

После запуска приложения документация API доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

#### 1. Парсинг статьи Wikipedia
```http
POST /api/wiki/parse
Content-Type: application/json

{
  "url": "https://ru.wikipedia.org/wiki/Питон_(язык_программирования)"
}
```

**Ответ:**
```json
{
  "article_id": "uuid-статьи"
}
```

#### 2. Получение summary статьи
```http
POST /api/wiki/summary
Content-Type: application/json

{
  "url": "https://ru.wikipedia.org/wiki/Питон_(язык_программирования)"
}
```

**Ответ:**
```json
{
  "article_id": "uuid",
  "title": "Название статьи",
  "url": "URL статьи",
  "summary": "Сгенерированное краткое содержание",
  "created_at": "Время создания"
}
```
