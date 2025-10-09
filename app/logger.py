# app/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name="rss_app", log_to_file=False, log_level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional file handler
    if log_to_file:
        log_dir = os.getenv("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        fh = RotatingFileHandler(f"{log_dir}/app.log", maxBytes=5_000_000, backupCount=2)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
