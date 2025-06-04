"""OpenTelemetry configuration for Azure Monitor and logging."""

import logging
import logging.config
import os
from trace.logging_config import LOGGING_CONFIG

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor


class OtelConfiguration:
    """
    Configuration class for OpenTelemetry and Azure Monitor.
    """

    _monitor_configured = False
    _logger_configured = False

    @classmethod
    def configure(cls) -> None:
        """
        Configures OpenTelemetry and Azure Monitor if not already configured.
        """
        if not cls._monitor_configured and os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
            configure_azure_monitor()
            logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
            logging.getLogger("azure.identity").setLevel(logging.WARNING)

            URLLib3Instrumentor().instrument()
            cls._monitor_configured = True

        if not cls._logger_configured:
            logging.config.dictConfig(LOGGING_CONFIG)
            cls._logger_configured = True
