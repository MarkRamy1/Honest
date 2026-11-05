import logging
import sys
from app.core.config import settings


def setup_logging():
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.ERROR)
    
    logger = logging.getLogger("honest_ai")
    logger.setLevel(level)
    return logger


logger = setup_logging()
