"""
Comprehensive logging system for the Tweet Thread Generator.

This module provides structured logging with proper formatting for GitHub Actions,
context information tracking, operation metrics, and security-aware logging
that prevents exposure of sensitive information.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum

from utils import is_github_actions_environment, get_repository_info


class LogLevel(str, Enum):
    """Log levels for structured logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OperationType(str, Enum):
    """Types of operations for tracking and metrics."""
    CONTENT_DETECTION = "content_detection"
    STYLE_ANALYSIS = "style_analysis"
    AI_GENERATION = "ai_generation"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    CONTENT_VALIDATION = "content_validation"
    PR_CREATION = "pr_creation"
    AUTO_POSTING = "auto_posting"
    FILE_OPERATION = "file_operation"
    API_CALL = "api_call"


@dataclass
class LogContext:
    """Context information for structured logging."""
    operation_type: Optional[OperationType] = None
    post_slug: Optional[str] = None
    model_used: Optional[str] = None
    thread_id: Optional[str] = None
    api_endpoint: Optional[str] = None
    file_path: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationMetrics:
    """Metrics for tracking operation performance and success rates."""
    operation_type: OperationType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    api_calls_made: int = 0
    tokens_used: int = 0
    characters_processed: int = 0
    files_created: int = 0
    files_modified: int = 0
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    def finish(self, success: bool = True, error: Optional[Exception] = None) -> None:
        """Mark operation as finished and calculate duration."""
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.success = success

        if error:
            self.error_type = type(error).__name__
            self.error_message = str(error)


class SensitiveDataFilter:
    """Filter to prevent logging of sensitive information."""

    SENSITIVE_PATTERNS = [
        # API keys and tokens
        r'(?i)(api[_-]?key|token|secret|password|auth)["\s]*[:=]["\s]*([a-zA-Z0-9+/=]{20,})',
        r'(?i)(bearer\s+)([a-zA-Z0-9+/=]{20,})',
        r'(?i)(authorization["\s]*[:=]["\s]*)([a-zA-Z0-9+/=]{20,})',
        # GitHub tokens
        r'(gh[ps]_[a-zA-Z0-9]{36})',
        # OpenRouter API keys
        r'(sk-or-[a-zA-Z0-9]{48})',
        # Twitter API keys
        r'([a-zA-Z0-9]{25})',
    ]

    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """Remove sensitive information from log messages."""
        import re

        sanitized = message
        for pattern in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, r'\1[REDACTED]', sanitized)

        return sanitized

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from dictionary data."""
        sanitized = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Check if key indicates sensitive data
            if any(sensitive in key_lower for sensitive in ['key', 'token', 'secret', 'password', 'auth']):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str):
                sanitized[key] = cls.sanitize_message(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_message(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


class StructuredLogger:
    """Main structured logger with context awareness and metrics tracking."""

    def __init__(self, name: str = "tweet_generator", log_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.log_level = log_level
        self.context_stack: List[LogContext] = []
        self.operation_metrics: List[OperationMetrics] = []
        self.session_id = self._generate_session_id()

        # Set up Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))

        # Configure handler if not already configured
        if not self.logger.handlers:
            self._setup_handler()

    def _generate_session_id(self) -> str:
        """Generate unique session ID for this logging session."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _setup_handler(self) -> None:
        """Set up logging handler with appropriate formatting."""
        handler = logging.StreamHandler(sys.stdout)

        if is_github_actions_environment():
            # GitHub Actions friendly format
            formatter = GitHubActionsFormatter()
        else:
            # Local development format with JSON structure
            formatter = JSONFormatter()

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Set levels for noisy dependencies
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('github').setLevel(logging.WARNING)
        logging.getLogger('tweepy').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

    def _get_current_context(self) -> Dict[str, Any]:
        """Get current logging context."""
        context = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "logger_name": self.name
        }

        # Add GitHub Actions context if available
        if is_github_actions_environment():
            repo_info = get_repository_info()
            context.update({
                "github_repository": repo_info.get("repository"),
                "github_ref": repo_info.get("ref"),
                "github_sha": repo_info.get("sha", "")[:8],
                "github_actor": repo_info.get("actor"),
                "github_run_id": repo_info.get("run_id"),
                "github_workflow": repo_info.get("workflow")
            })

        # Add context from stack
        if self.context_stack:
            current_ctx = self.context_stack[-1]
            if current_ctx.operation_type:
                context["operation_type"] = current_ctx.operation_type.value
            if current_ctx.post_slug:
                context["post_slug"] = current_ctx.post_slug
            if current_ctx.model_used:
                context["model_used"] = current_ctx.model_used
            if current_ctx.thread_id:
                context["thread_id"] = current_ctx.thread_id
            if current_ctx.api_endpoint:
                context["api_endpoint"] = current_ctx.api_endpoint
            if current_ctx.file_path:
                context["file_path"] = current_ctx.file_path

            # Add additional context
            context.update(current_ctx.additional_context)

        return context

    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal logging method with context and sanitization."""
        # Sanitize message and kwargs
        sanitized_message = SensitiveDataFilter.sanitize_message(message)
        sanitized_kwargs = SensitiveDataFilter.sanitize_dict(kwargs)

        # Get context
        context = self._get_current_context()
        context.update(sanitized_kwargs)

        # Log with appropriate level
        log_method = getattr(self.logger, level.value.lower())
        log_method(sanitized_message, extra={"context": context})

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log error message with optional exception details."""
        if error:
            kwargs.update({
                "error_type": type(error).__name__,
                "error_message": str(error)
            })

            # Add stack trace in debug mode
            if self.log_level == LogLevel.DEBUG:
                import traceback
                kwargs["stack_trace"] = traceback.format_exc()

        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log critical message."""
        if error:
            kwargs.update({
                "error_type": type(error).__name__,
                "error_message": str(error)
            })

        self._log(LogLevel.CRITICAL, message, **kwargs)

    @contextmanager
    def operation_context(self, operation_type: OperationType, **context_kwargs):
        """Context manager for operation-specific logging."""
        # Separate known LogContext fields from additional context
        known_fields = {
            'post_slug', 'model_used', 'thread_id', 'api_endpoint',
            'file_path', 'user_id', 'session_id'
        }

        # Extract known fields
        context_fields = {}
        additional_context = {}

        for key, value in context_kwargs.items():
            if key in known_fields:
                context_fields[key] = value
            else:
                additional_context[key] = value

        # Create context
        context = LogContext(
            operation_type=operation_type,
            additional_context=additional_context,
            **context_fields
        )

        # Create metrics tracker
        metrics = OperationMetrics(
            operation_type=operation_type,
            start_time=datetime.now(timezone.utc)
        )

        self.context_stack.append(context)
        self.operation_metrics.append(metrics)

        try:
            self.info(f"Starting {operation_type.value} operation")
            yield metrics
            metrics.finish(success=True)
            self.info(f"Completed {operation_type.value} operation",
                     duration_ms=metrics.duration_ms)
        except Exception as e:
            metrics.finish(success=False, error=e)
            self.error(f"Failed {operation_type.value} operation",
                      error=e, duration_ms=metrics.duration_ms)
            raise
        finally:
            self.context_stack.pop()

    def log_api_call(self, endpoint: str, method: str = "POST",
                    response_time_ms: Optional[float] = None,
                    status_code: Optional[int] = None,
                    tokens_used: Optional[int] = None,
                    error: Optional[Exception] = None) -> None:
        """Log API call with performance metrics."""
        log_data = {
            "api_endpoint": endpoint,
            "http_method": method,
        }

        if response_time_ms is not None:
            log_data["response_time_ms"] = response_time_ms
        if status_code is not None:
            log_data["status_code"] = status_code
        if tokens_used is not None:
            log_data["tokens_used"] = tokens_used

        if error:
            self.error(f"API call failed: {method} {endpoint}", error=error, **log_data)
        else:
            self.info(f"API call successful: {method} {endpoint}", **log_data)

    def log_file_operation(self, operation: str, file_path: str,
                          success: bool = True, error: Optional[Exception] = None) -> None:
        """Log file operations."""
        log_data = {
            "file_operation": operation,
            "file_path": file_path,
            "success": success
        }

        if error:
            self.error(f"File operation failed: {operation} {file_path}",
                      error=error, **log_data)
        else:
            self.info(f"File operation successful: {operation} {file_path}", **log_data)

    def log_content_processing(self, content_type: str, item_count: int,
                             characters_processed: int = 0,
                             processing_time_ms: Optional[float] = None) -> None:
        """Log content processing metrics."""
        log_data = {
            "content_type": content_type,
            "items_processed": item_count,
            "characters_processed": characters_processed
        }

        if processing_time_ms is not None:
            log_data["processing_time_ms"] = processing_time_ms

        self.info(f"Processed {item_count} {content_type} items", **log_data)

    def get_session_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for the current session."""
        total_operations = len(self.operation_metrics)
        successful_operations = sum(1 for m in self.operation_metrics if m.success)
        failed_operations = total_operations - successful_operations

        # Calculate operation type breakdown
        operation_breakdown = {}
        for metrics in self.operation_metrics:
            op_type = metrics.operation_type.value
            if op_type not in operation_breakdown:
                operation_breakdown[op_type] = {"total": 0, "successful": 0, "failed": 0}

            operation_breakdown[op_type]["total"] += 1
            if metrics.success:
                operation_breakdown[op_type]["successful"] += 1
            else:
                operation_breakdown[op_type]["failed"] += 1

        # Calculate timing metrics
        completed_operations = [m for m in self.operation_metrics if m.duration_ms is not None]
        avg_duration = (
            sum(m.duration_ms for m in completed_operations) / len(completed_operations)
            if completed_operations else 0
        )

        # Calculate resource usage
        total_api_calls = sum(m.api_calls_made for m in self.operation_metrics)
        total_tokens = sum(m.tokens_used for m in self.operation_metrics)
        total_characters = sum(m.characters_processed for m in self.operation_metrics)
        total_files_created = sum(m.files_created for m in self.operation_metrics)
        total_files_modified = sum(m.files_modified for m in self.operation_metrics)

        return {
            "session_id": self.session_id,
            "session_start": self.operation_metrics[0].start_time.isoformat() if self.operation_metrics else None,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            "average_operation_duration_ms": avg_duration,
            "operation_breakdown": operation_breakdown,
            "resource_usage": {
                "api_calls_made": total_api_calls,
                "tokens_used": total_tokens,
                "characters_processed": total_characters,
                "files_created": total_files_created,
                "files_modified": total_files_modified
            }
        }

    def save_session_metrics(self, output_path: str) -> None:
        """Save session metrics to file."""
        metrics = self.get_session_metrics()

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, default=str)
            self.info(f"Session metrics saved to {output_path}")
        except Exception as e:
            self.error(f"Failed to save session metrics", error=e)


class GitHubActionsFormatter(logging.Formatter):
    """Formatter for GitHub Actions environment."""

    def format(self, record):
        # GitHub Actions format: LEVEL: message
        level_prefix = ""
        if record.levelno >= logging.ERROR:
            level_prefix = "::error::"
        elif record.levelno >= logging.WARNING:
            level_prefix = "::warning::"

        message = super().format(record)

        # Add context information if available
        if hasattr(record, 'context'):
            context = record.context

            # Add key context items to the message
            context_items = []
            if 'operation_type' in context:
                context_items.append(f"op={context['operation_type']}")
            if 'post_slug' in context:
                context_items.append(f"post={context['post_slug']}")
            if 'duration_ms' in context:
                context_items.append(f"duration={context['duration_ms']:.1f}ms")

            if context_items:
                message += f" [{', '.join(context_items)}]"

        return f"{level_prefix}{message}"


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in development."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        # Add context if available
        if hasattr(record, 'context'):
            log_entry["context"] = record.context

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


# Global logger instance
_global_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "tweet_generator") -> StructuredLogger:
    """Get or create global logger instance."""
    global _global_logger

    if _global_logger is None:
        # Determine log level from environment
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            log_level = LogLevel(log_level_str)
        except ValueError:
            log_level = LogLevel.INFO

        _global_logger = StructuredLogger(name=name, log_level=log_level)

    return _global_logger


def setup_logging(name: str = "tweet_generator", log_level: Optional[LogLevel] = None) -> StructuredLogger:
    """Set up and configure logging for the application."""
    global _global_logger

    if log_level is None:
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            log_level = LogLevel(log_level_str)
        except ValueError:
            log_level = LogLevel.INFO

    _global_logger = StructuredLogger(name=name, log_level=log_level)

    # Log initialization
    _global_logger.info("Logging system initialized",
                       log_level=log_level.value,
                       github_actions=is_github_actions_environment())

    return _global_logger


# Convenience functions for common logging patterns
def log_operation_start(operation_type: OperationType, **context) -> None:
    """Log the start of an operation."""
    logger = get_logger()
    with logger.operation_context(operation_type, **context):
        pass


def log_api_call(endpoint: str, method: str = "POST", **kwargs) -> None:
    """Log an API call."""
    logger = get_logger()
    logger.log_api_call(endpoint, method, **kwargs)


def log_file_operation(operation: str, file_path: str, **kwargs) -> None:
    """Log a file operation."""
    logger = get_logger()
    logger.log_file_operation(operation, file_path, **kwargs)


def log_content_processing(content_type: str, item_count: int, **kwargs) -> None:
    """Log content processing."""
    logger = get_logger()
    logger.log_content_processing(content_type, item_count, **kwargs)