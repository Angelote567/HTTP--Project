from __future__ import annotations

import logging
import logging.handlers
import time
from pathlib import Path
from typing import Optional

from .http_messages import Response
from .middleware import Handler, RequestContext

LOGGER_NAME = "usj_http"


def configure_logger(
    log_file: Optional[str] = None,
    level: str = "INFO",
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        rotating = logging.handlers.RotatingFileHandler(
            filename=str(path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        rotating.setFormatter(fmt)
        logger.addHandler(rotating)

    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def logging_middleware(ctx: RequestContext, next_handler: Handler) -> Response:
    logger = get_logger()
    start = time.perf_counter()
    logger.info("--> %s %s", ctx.method, ctx.target)
    try:
        response = next_handler(ctx)
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.exception("xx %s %s failed after %.1f ms", ctx.method, ctx.target, elapsed_ms)
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "<-- %s %s %s in %.1f ms",
        ctx.method,
        ctx.target,
        response.status_code,
        elapsed_ms,
    )
    return response
