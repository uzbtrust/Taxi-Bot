import sys
from loguru import logger
from config import settings


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    )
    logger.add(
        "logs/bot.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
    )


def mask_phone(phone: str) -> str:
    if len(phone) >= 8:
        return phone[:4] + "***" + phone[-2:]
    return "***"
