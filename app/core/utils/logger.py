import logging

from core.config import settings


def setup_logger():
    logger = logging.getLogger(settings.logger.logger_name)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
    )

    # Файловый хендлер
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    log_level = getattr(logging, settings.logger.log_info)
    logger.setLevel(log_level)

    logger.propagate = False

    logger.info("Logger successfully initialized")
    logger.debug("Log level: %s", settings.logger.log_info)
