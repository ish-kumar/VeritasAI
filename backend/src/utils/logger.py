"""
Logging configuration using loguru.

Why loguru over standard logging:
- Simpler API
- Better formatting out of the box
- Automatic exception tracing
- Async-safe

Production logging requirements:
- Log all agent decisions
- Log confidence scores
- Log refusals (for analysis)
- Never log PII or sensitive content
"""

import sys
from loguru import logger
from .config import get_settings


def setup_logger():
    """
    Configure logger for the application.
    
    Design decisions:
    1. Console output for development
    2. File output for production (with rotation)
    3. JSON format for production (for log aggregation)
    4. Separate error log file
    
    Why structured logging matters:
    - Easy to parse with tools (CloudWatch, Datadog)
    - Can search by query_id
    - Can track confidence over time
    """
    settings = get_settings()
    
    # Remove default logger
    logger.remove()
    
    # Console logger (for development)
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=settings.log_level,
    )
    
    # File logger (for production)
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
    )
    
    # Error logger (separate file for errors)
    logger.add(
        "logs/errors.log",
        rotation="500 MB",
        retention="30 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
        backtrace=True,
        diagnose=True,
    )
    
    return logger


def log_agent_execution(agent_name: str, input_data: dict, output_data: dict, duration_ms: float):
    """
    Log agent execution for audit trail.
    
    Why this matters:
    - Debug agent failures
    - Measure performance
    - Audit legal decisions
    """
    logger.info(
        f"Agent executed: {agent_name}",
        extra={
            "agent": agent_name,
            "duration_ms": duration_ms,
            "input_keys": list(input_data.keys()),
            "output_keys": list(output_data.keys()),
        }
    )


def log_refusal(query_id: str, reason: str, confidence: float):
    """
    Log when we refuse to answer.
    
    Why track refusals:
    - Measure system coverage
    - Identify missing documents
    - Tune confidence thresholds
    """
    logger.warning(
        f"Query refused: {query_id}",
        extra={
            "query_id": query_id,
            "reason": reason,
            "confidence": confidence,
        }
    )

