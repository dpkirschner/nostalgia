import logging
import sys
from contextlib import contextmanager
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


class CorrelationIdFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.correlation_id: Optional[str] = None

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self.correlation_id or "N/A"
        return True


_correlation_filter = CorrelationIdFilter()


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(correlation_id)s %(message)s",
            timestamp=True,
        )
    else:
        try:
            import colorlog

            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        except ImportError:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

    handler.setFormatter(formatter)
    handler.addFilter(_correlation_filter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_correlation_id(correlation_id: Optional[str]) -> None:
    _correlation_filter.correlation_id = correlation_id


@contextmanager
def log_context(**kwargs: Any):
    logger = logging.getLogger()
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args: Any, **record_kwargs: Any) -> logging.LogRecord:
        record = old_factory(*args, **record_kwargs)
        for key, value in kwargs.items():
            setattr(record, key, value)
        return record

    logging.setLogRecordFactory(record_factory)
    try:
        yield
    finally:
        logging.setLogRecordFactory(old_factory)
