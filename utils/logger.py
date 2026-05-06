import sys
from loguru import logger
from config import settings


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="{time:HH:mm:ss} | {level: <8} | {name} - {message}",
        colorize=False,
    )


def mask_phone(phone: str) -> str:
    if len(phone) >= 8:
        return phone[:4] + "***" + phone[-2:]
    return "***"
