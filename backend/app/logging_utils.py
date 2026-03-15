import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import Settings


APP_LOGGER_NAME = "story_writers"
AUDIT_LOGGER_NAME = "story_writers.audit"


def configure_logging(settings: Settings) -> None:
    log_dir = Path(settings.log_dir)
    if not log_dir.is_absolute():
        log_dir = Path.cwd() / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    app_logger = logging.getLogger(APP_LOGGER_NAME)
    audit_logger = logging.getLogger(AUDIT_LOGGER_NAME)
    root_logger = logging.getLogger()

    for logger in (app_logger, audit_logger, root_logger):
        logger.handlers.clear()

    app_logger.setLevel(level)
    audit_logger.setLevel(logging.INFO)
    root_logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    app_file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    app_file_handler.setLevel(level)
    app_file_handler.setFormatter(formatter)

    audit_file_handler = RotatingFileHandler(
        log_dir / "audit.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    audit_file_handler.setLevel(logging.INFO)
    audit_file_handler.setFormatter(formatter)

    app_logger.addHandler(console_handler)
    app_logger.addHandler(app_file_handler)
    app_logger.propagate = False

    audit_logger.addHandler(audit_file_handler)
    audit_logger.addHandler(console_handler)
    audit_logger.propagate = False

    root_logger.addHandler(console_handler)


def get_logger(name: str | None = None) -> logging.Logger:
    base_name = APP_LOGGER_NAME if not name else f"{APP_LOGGER_NAME}.{name}"
    return logging.getLogger(base_name)


def get_audit_logger() -> logging.Logger:
    return logging.getLogger(AUDIT_LOGGER_NAME)
