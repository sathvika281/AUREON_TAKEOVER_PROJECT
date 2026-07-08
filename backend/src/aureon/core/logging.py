import logging
import sys

import structlog

from aureon.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure structlog + stdlib logging once, at application startup.

    JSON rendering in staging/production for machine-readable log
    aggregation; colored console rendering in local dev. Callers get a
    logger via ``structlog.get_logger(__name__)`` and use ``.bind(...)`` to
    attach request-scoped context (e.g. conversation_id, agent name) so logs
    correlate across the orchestrator without threading context manually
    through every function call.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level.upper(),
    )

    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_format == "json":
        renderer: structlog.typing.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
