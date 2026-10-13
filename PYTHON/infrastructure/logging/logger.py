import logging
from datetime import datetime, timedelta, timezone


class CustomTZFormatter(logging.Formatter):
    def __init__(self, tz_offset_hours=-5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tz = timezone(timedelta(hours=tz_offset_hours))

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        return dt.strftime(datefmt) if datefmt else dt.isoformat()


def get_logger(name: str, level=logging.DEBUG, tz_offset_hours=-5) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)

        formatter = CustomTZFormatter(
            tz_offset_hours=tz_offset_hours, fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
