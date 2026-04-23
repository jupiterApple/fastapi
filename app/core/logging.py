import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    backtrace=True,
    diagnose=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan> | <level>{message}</level>",
)
