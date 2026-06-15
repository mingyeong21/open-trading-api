import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")


class KSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, KST)

        if datefmt:
            return dt.strftime(datefmt)

        return dt.strftime("%Y-%m-%d %H:%M:%S")


def setup_logger() -> logging.Logger:
    """
    Set up a simple console + file logger using Korea Standard Time.
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("samsung_auto_trader")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = KSTFormatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        logs_dir / "trading.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()