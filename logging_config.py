import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,  # or INFO in production
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # console
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),  # main log
        logging.FileHandler(os.path.join(LOG_DIR, "errors.log")),  # errors only
    ]
)

# Create separate loggers if needed
logger = logging.getLogger("ai_scraper")
error_logger = logging.getLogger("ai_scraper.errors")
error_logger.setLevel(logging.ERROR)
