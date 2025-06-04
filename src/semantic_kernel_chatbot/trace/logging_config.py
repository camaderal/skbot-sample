"""Logging configuration for the Semantic Kernel Chatbot project."""

import logging
from typing import Any


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter to include logger name in the log record.
    """

    def format(self, record: Any) -> str:
        """
        Format the log record to include the logger name.

        Args:
            record (Any): The log record to format.

        Returns:
            str: The formatted log record.

        """
        record.logger_name = record.name
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "()": CustomFormatter,
            "format": "%(asctime)s - %(levelname)s - [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
        },
        "opentelemetry": {
            "level": "INFO",
            "class": "opentelemetry.sdk._logs.LoggingHandler",
            "formatter": "default_formatter",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "opentelemetry"],
    },
}
