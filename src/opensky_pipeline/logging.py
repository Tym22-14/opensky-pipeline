import logging

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Set up structured JSON logging for the project.
    Call once at the top of each script or Airflow task.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # pulls in task_id, dag_id etc.
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level)),
        logger_factory=structlog.PrintLoggerFactory(),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Return a named logger. Use at the top of every module:

        from opensky_pipeline.logging import get_logger
        logger = get_logger(__name__)
        logger.info("something happened", records=672)
    """
    return structlog.get_logger(name)
