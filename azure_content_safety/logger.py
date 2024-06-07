import logging
import os
import time
from typing import List

from rich.logging import RichHandler


def get_logger(name: str, logger_blocklist: List[str] = []):
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)

    format = '%(asctime)s | %(levelname)7s | %(name)s | %(message)s'
    # format="%(message)s"

    logging.basicConfig(
        format=format,
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=False)],
    )
    logging.Formatter.converter = time.gmtime  # Enforce UTC timestamps

    logger = logging.getLogger(name)

    return logger
