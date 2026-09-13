import logging
import sys
from config.settings import settings
LOG_FORMAT="%(asctime)s | %(levelname)s | %(name)s | %(message)s"

log_level = getattr(
    logging,
    settings. log_level.upper(),
    logging.INFO,
)
logging.basicConfig(
    level=log_level,
    format=LOG_FORMAT,
    stream=sys.stdout,
)
logger=logging.getLogger("agentic-sdlc")