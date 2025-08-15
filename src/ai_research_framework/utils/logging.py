"""Enhanced logging configuration using Loguru."""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from ..config import settings


def setup_logging() -> None:
    """Configure Loguru logging for the application."""
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler for all logs
    logger.add(
        log_dir / "ai_research_framework.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Error file handler
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="5 MB",
        retention="60 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Research operations log
    logger.add(
        log_dir / "research_operations.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[operation_type]} | {message}",
        filter=lambda record: "operation_type" in record["extra"],
        rotation="20 MB",
        retention="90 days",
        compression="zip"
    )
    
    logger.info("Logging system initialized with Loguru")


def get_logger(name: str) -> Any:
    """Get a logger instance with the specified name."""
    return logger.bind(name=name)


def log_research_operation(operation_type: str, message: str, **kwargs) -> None:
    """Log research operations with structured data."""
    logger.bind(operation_type=operation_type).info(message, **kwargs)


def log_performance(endpoint: str, duration_ms: float, **kwargs) -> None:
    """Log performance metrics."""
    logger.bind(endpoint=endpoint, duration=duration_ms).info(
        f"Request completed in {duration_ms}ms", **kwargs
    )


def log_api_request(method: str, path: str, status_code: int, duration_ms: float, **kwargs) -> None:
    """Log API requests with structured data."""
    logger.bind(
        method=method,
        path=path,
        status_code=status_code,
        duration=duration_ms
    ).info(f"{method} {path} - {status_code} ({duration_ms}ms)", **kwargs)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self):
        """Get logger instance for this class."""
        return logger.bind(name=self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)


def configure_uvicorn_logging():
    """Configure Uvicorn to use Loguru."""
    import logging
    
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Replace standard logging with Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


class LogContext:
    """Context manager for structured logging."""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        logger.bind(**self.context).info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            logger.bind(**self.context, duration=duration).info(
                f"Completed {self.operation} in {duration:.2f}ms"
            )
        else:
            logger.bind(**self.context, duration=duration).error(
                f"Failed {self.operation} after {duration:.2f}ms: {exc_val}"
            )

