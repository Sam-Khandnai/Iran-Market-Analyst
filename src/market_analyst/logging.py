import logging
import sys

import structlog


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(message)s", level=level.upper(), stream=sys.stderr,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )


def get_logger(name: str = "market_analyst"):
    return structlog.get_logger(name)