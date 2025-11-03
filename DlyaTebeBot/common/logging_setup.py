import os
import sys
import logging
from loguru import logger

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger.remove()  
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = record.levelname
        except Exception:
            level = "INFO"
        logger.opt(exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=LOG_LEVEL)

def setup_logger():
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("aiohttp").handlers = [InterceptHandler()]
    logging.getLogger("django").handlers = [InterceptHandler()]
    return logger
