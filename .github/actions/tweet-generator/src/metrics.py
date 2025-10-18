"""
Metrics collection and monitoring system for the Tweet Thread Generator.

This module provides comprehensive metrics tracking including API response times,
content generation success rates, performance metrics, error tracking, and
GitHub Actions output metrics.
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import contextmanager
from enum import Enum

from logger import get_logger, OperationType


class MetricType(str, Enum):
    """Types of metrics being tracked."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ErrorCategory(str, Enum):
    """Categories of errors for tracking and analysis."""
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    CONTENT_ERROR = "content_error"
    FILE_ERROR = "file_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class MetricPoint:
    """Individual metric data point."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class APIMetrics:
    """Metrics for API calls and performance."""
    endpoint: str
    method: str = "POST"
    response_time_ms: float = 0.0
    status_code: Optional[int] = None
    tokens_used: int = 0
    tokens_requested: int = 0
    success: bool = True
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "response_time_ms": self.response_time_ms,
            "status_code": self.status_code,
            "tokens_used": self.tokens_used,
            "tokens_requested": self.tokens_requested,
            "success": self.success,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ContentGenerationMetrics:
    """Metrics for content generation operations."""
    operation_type: OperationType
    post_slug: str
    model_used: str
    input_characters: int = 0
    output_characters: int = 0
    processing_time_ms: float = 0.0
    tweets_generated: int = 0
    hooks_generated: int = 0
    engagement_score: float = 0.0
    validation_passed: bool = True
    success: bool = True
    error_type: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_type": self.operation_type.value,
            "post_slug": self.post_slug,
            "model_used": self.model_used,
            "input_characters": self.input_characters,
            "output_characters": self.output_characters,
            "processing_time_ms": self.processing_time_ms,
            "tweets_generated": self.tweets_generated,
            "hooks_generated": self.hooks_generated,
            "engagement_score": self.engagement_score,
            "validation_passed": self.validation_passed,
            "success": self.success,
            "error_type": self.error_type,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ErrorMetrics:
    """Metrics for error tracking and categorization."""
    error_category: ErrorCategory
    error_type: str
    error_message: str
    operation_type: Optional[OperationType] = None
    post_slug: Optional[str] = None
    api_endpoint: Optional[str] = None
    file_path: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "error_category": self.error_category.value,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "operation_type": self.operation_type.value if self.operation_type else None,
            "post_slug": self.post_slug,
            "api_endpoint": self.api_endpoint,
            "file_path": self.file_path,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for system optimization."""
    operation_type: OperationType
    duration_ms: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    files_processed: int = 0
    characters_processed: int = 0
    api_calls_made: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_type": self.operation_type.value,
            "duration_ms": self.duration_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "files_processed": self.files_processed,
            "characters_processed": self.characters_processed,
            "api_calls_made": self.api_calls_made,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "timestamp": self.timestamp.isoformat()
        }


class MetricsCollector:
    """Main metrics collection and aggregation system."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.logger = get_logger()

        # Metric storage
        self.metrics: List[MetricPoint] = []
        self.api_metrics: List[APIMetrics] = []
        self.content_metrics: List[ContentGenerationMetrics] = []
        self.error_metrics: List[ErrorMetrics] = []
        self.performance_metrics: List[PerformanceMetrics] = []

        # Counters and gauges
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.timers: Dict[str, List[float]] = {}

        # Session tracking
        self.session_start = datetime.now(timezone.utc)
        self.operations_completed = 0
        self.operations_failed = 0

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        self.counters[name] = self.counters.get(name, 0) + value

        metric = MetricPoint(
            name=name,
            value=self.counters[name],
            metric_type=MetricType.COUNTER,
            tags=tags or {}
        )
        self.metrics.append(metric)

        self.logger.debug(f"Counter incremented: {name} = {self.counters[name]}")

    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        self.gauges[name] = value

        metric = MetricPoint(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {}
        )
        self.metrics.append(metric)

        self.logger.debug(f"Gauge set: {name} = {value}")

    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing measurement."""
        if name not in self.timers:
            self.timers[name] = []
        self.timers[name].append(duration_ms)

        metric = MetricPoint(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            tags=tags or {}
        )
        self.metrics.append(metric)

        self.logger.debug(f"Timer recorded: {name} = {duration_ms}ms")

    @contextmanager
    def time_operation(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.record_timer(operation_name, duration_ms, tags)

    def record_api_call(self, endpoint: str, method: str = "POST",
                       response_time_ms: float = 0.0,
                       status_code: Optional[int] = None,
                       tokens_used: int = 0,
                       tokens_requested: int = 0,
                       success: bool = True,
                       error: Optional[Exception] = None) -> None:
        """Record API call metrics."""
        api_metric = APIMetrics(
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=status_code,
            tokens_used=tokens_used,
            tokens_requested=tokens_requested,
            success=success,
            error_type=type(error).__name__ if error else None,
            error_message=str(error) if error else None
        )

        self.api_metrics.append(api_metric)

        # Update counters
        self.increment_counter("api_calls_total")
        if success:
            self.increment_counter("api_calls_successful")
        else:
            self.increment_counter("api_calls_failed")

        # Update gauges
        self.set_gauge("api_response_time_ms", response_time_ms)
        if tokens_used > 0:
            self.increment_counter("tokens_used_total", tokens_used)

        self.logger.info(f"API call recorded: {method} {endpoint}",
                        response_time_ms=response_time_ms,
                        success=success,
                        tokens_used=tokens_used)

    def record_content_generation(self, operation_type: OperationType,
                                post_slug: str,
                                model_used: str,
                                input_characters: int = 0,
                                output_characters: int = 0,
                                processing_time_ms: float = 0.0,
                                tweets_generated: int = 0,
                                hooks_generated: int = 0,
                                engagement_score: float = 0.0,
                                validation_passed: bool = True,
                                success: bool = True,
                                error: Optional[Exception] = None) -> None:
        """Record content generation metrics."""
        content_metric = ContentGenerationMetrics(
            operation_type=operation_type,
            post_slug=post_slug,
            model_used=model_used,
            input_characters=input_characters,
            output_characters=output_characters,
            processing_time_ms=processing_time_ms,
            tweets_generated=tweets_generated,
            hooks_generated=hooks_generated,
            engagement_score=engagement_score,
            validation_passed=validation_passed,
            success=success,
            error_type=type(error).__name__ if error else None
        )

        self.content_metrics.append(content_metric)

        # Update counters
        self.increment_counter("content_generation_total")
        if success:
            self.increment_counter("content_generation_successful")
            self.increment_counter("tweets_generated_total", tweets_generated)
            self.increment_counter("hooks_generated_total", hooks_generated)
        else:
            self.increment_counter("content_generation_failed")

        # Update gauges
        self.set_gauge("content_processing_time_ms", processing_time_ms)
        self.set_gauge("engagement_score", engagement_score)

        self.logger.info(f"Content generation recorded: {operation_type.value}",
                        post_slug=post_slug,
                        model_used=model_used,
                        success=success,
                        tweets_generated=tweets_generated)

    def record_error(self, error_category: ErrorCategory,
                    error: Exception,
                    operation_type: Optional[OperationType] = None,
                    post_slug: Optional[str] = None,
                    api_endpoint: Optional[str] = None,
                    file_path: Optional[str] = None,
                    recovery_attempted: bool = False,
                    recovery_successful: bool = False) -> None:
        """Record error metrics."""
        error_metric = ErrorMetrics(
            error_category=error_category,
            error_type=type(error).__name__,
            error_message=str(error),
            operation_type=operation_type,
            post_slug=post_slug,
            api_endpoint=api_endpoint,
            file_path=file_path,
            recovery_attempted=recovery_attempted,
            recovery_successful=recovery_successful
        )

        self.error_metrics.append(error_metric)

        # Update counters
        self.increment_counter("errors_total")
        self.increment_counter(f"errors_{error_category.value}")
        self.increment_counter(f"errors_{type(error).__name__.lower()}")

        if recovery_attempted:
            self.increment_counter("error_recovery_attempted")
            if recovery_successful:
                self.increment_counter("error_recovery_successful")

        self.logger.error(f"Error recorded: {error_category.value}",
                         error=error,
                         operation_type=operation_type.value if operation_type else None,
                         post_slug=post_slug)

    def record_performance(self, operation_type: OperationType,
                          duration_ms: float,
                          memory_usage_mb: Optional[float] = None,
                          cpu_usage_percent: Optional[float] = None,
                          files_processed: int = 0,
                          characters_processed: int = 0,
                          api_calls_made: int = 0,
                          cache_hits: int = 0,
                          cache_misses: int = 0) -> None:
        """Record comprehensive performance metrics."""
        # Get system resource usage if not provided
        if memory_usage_mb is None or cpu_usage_percent is None:
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())

                if memory_usage_mb is None:
                    memory_usage_mb = process.memory_info().rss / 1024 / 1024
                if cpu_usage_percent is None:
                    cpu_usage_percent = process.cpu_percent()
            except ImportError:
                # psutil not available, use None values
                pass

        perf_metric = PerformanceMetrics(
            operation_type=operation_type,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            files_processed=files_processed,
            characters_processed=characters_processed,
            api_calls_made=api_calls_made,
            cache_hits=cache_hits,
            cache_misses=cache_misses
        )

        self.performance_metrics.append(perf_metric)

        # Update counters and gauges
        self.increment_counter(f"performance_{operation_type.value}_operations")
        self.set_gauge(f"performance_{operation_type.value}_duration_ms", duration_ms)

        if memory_usage_mb is not None:
            self.set_gauge("memory_usage_mb", memory_usage_mb)
        if cpu_usage_percent is not None:
            self.set_gauge("cpu_usage_percent", cpu_usage_percent)

        # Track cache efficiency
        if cache_hits > 0 or cache_misses > 0:
            cache_hit_rate = cache_hits / (cache_hits + cache_misses) * 100
            self.set_gauge(f"cache_hit_rate_{operation_type.value}", cache_hit_rate)

        # Track processing efficiency
        if characters_processed > 0 and duration_ms > 0:
            chars_per_second = (characters_processed / duration_ms) * 1000
            self.set_gauge(f"processing_speed_{operation_type.value}_chars_per_sec", chars_per_second)

        self.logger.info(f"Performance recorded: {operation_type.value}",
                        duration_ms=duration_ms,
                        files_processed=files_processed,
                        characters_processed=characters_processed,
                        memory_usage_mb=memory_usage_mb,
                        cpu_usage_percent=cpu_usage_percent,
                        cache_hit_rate=cache_hits / (cache_hits + cache_misses) * 100 if (cache_hits + cache_misses) > 0 else None)

    def get_api_statistics(self) -> Dict[str, Any]:
        """Get API call statistics."""
        if not self.api_metrics:
            return {}

        successful_calls = [m for m in self.api_metrics if m.success]
        failed_calls = [m for m in self.api_metrics if not m.success]

        response_times = [m.response_time_ms for m in self.api_metrics if m.response_time_ms > 0]

        stats = {
            "total_calls": len(self.api_metrics),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "success_rate": (len(successful_calls) / len(self.api_metrics) * 100) if self.api_metrics else 0,
            "total_tokens_used": sum(m.tokens_used for m in self.api_metrics),
            "average_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0
        }

        # Endpoint breakdown
        endpoint_stats = {}
        for metric in self.api_metrics:
            endpoint = metric.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"calls": 0, "successful": 0, "failed": 0, "avg_response_time": 0}

            endpoint_stats[endpoint]["calls"] += 1
            if metric.success:
                endpoint_stats[endpoint]["successful"] += 1
            else:
                endpoint_stats[endpoint]["failed"] += 1

        # Calculate average response times per endpoint
        for endpoint in endpoint_stats:
            endpoint_metrics = [m for m in self.api_metrics if m.endpoint == endpoint and m.response_time_ms > 0]
            if endpoint_metrics:
                endpoint_stats[endpoint]["avg_response_time"] = (
                    sum(m.response_time_ms for m in endpoint_metrics) / len(endpoint_metrics)
                )

        stats["endpoint_breakdown"] = endpoint_stats

        return stats

    def get_content_statistics(self) -> Dict[str, Any]:
        """Get content generation statistics."""
        if not self.content_metrics:
            return {}

        successful_generations = [m for m in self.content_metrics if m.success]
        failed_generations = [m for m in self.content_metrics if not m.success]

        stats = {
            "total_generations": len(self.content_metrics),
            "successful_generations": len(successful_generations),
            "failed_generations": len(failed_generations),
            "success_rate": (len(successful_generations) / len(self.content_metrics) * 100) if self.content_metrics else 0,
            "total_tweets_generated": sum(m.tweets_generated for m in successful_generations),
            "total_hooks_generated": sum(m.hooks_generated for m in successful_generations),
            "average_engagement_score": (
                sum(m.engagement_score for m in successful_generations) / len(successful_generations)
                if successful_generations else 0
            ),
            "average_processing_time_ms": (
                sum(m.processing_time_ms for m in self.content_metrics) / len(self.content_metrics)
                if self.content_metrics else 0
            )
        }

        # Operation type breakdown
        operation_stats = {}
        for metric in self.content_metrics:
            op_type = metric.operation_type.value
            if op_type not in operation_stats:
                operation_stats[op_type] = {"total": 0, "successful": 0, "failed": 0}

            operation_stats[op_type]["total"] += 1
            if metric.success:
                operation_stats[op_type]["successful"] += 1
            else:
                operation_stats[op_type]["failed"] += 1

        stats["operation_breakdown"] = operation_stats

        return stats

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics and categorization."""
        if not self.error_metrics:
            return {
                "total_errors": 0,
                "category_breakdown": {},
                "error_type_breakdown": {},
                "recovery_attempted": 0,
                "recovery_successful": 0,
                "recovery_success_rate": 0,
                "error_rate_by_operation": {},
                "recent_errors": []
            }

        # Category breakdown
        category_stats = {}
        for metric in self.error_metrics:
            category = metric.error_category.value
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1

        # Error type breakdown
        error_type_stats = {}
        for metric in self.error_metrics:
            error_type = metric.error_type
            if error_type not in error_type_stats:
                error_type_stats[error_type] = 0
            error_type_stats[error_type] += 1

        # Operation type error breakdown
        operation_error_stats = {}
        for metric in self.error_metrics:
            if metric.operation_type:
                op_type = metric.operation_type.value
                if op_type not in operation_error_stats:
                    operation_error_stats[op_type] = 0
                operation_error_stats[op_type] += 1

        # Recovery statistics
        recovery_attempted = sum(1 for m in self.error_metrics if m.recovery_attempted)
        recovery_successful = sum(1 for m in self.error_metrics if m.recovery_successful)

        # Recent errors (last 10)
        recent_errors = sorted(self.error_metrics, key=lambda x: x.timestamp, reverse=True)[:10]
        recent_error_data = [
            {
                "category": error.error_category.value,
                "type": error.error_type,
                "message": error.error_message[:100] + "..." if len(error.error_message) > 100 else error.error_message,
                "operation": error.operation_type.value if error.operation_type else None,
                "timestamp": error.timestamp.isoformat()
            }
            for error in recent_errors
        ]

        return {
            "total_errors": len(self.error_metrics),
            "category_breakdown": category_stats,
            "error_type_breakdown": error_type_stats,
            "error_rate_by_operation": operation_error_stats,
            "recovery_attempted": recovery_attempted,
            "recovery_successful": recovery_successful,
            "recovery_success_rate": (recovery_successful / recovery_attempted * 100) if recovery_attempted > 0 else 0,
            "recent_errors": recent_error_data
        }

    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        if not self.performance_metrics:
            return {
                "total_operations": 0,
                "operation_breakdown": {},
                "average_metrics": {},
                "resource_usage": {},
                "efficiency_metrics": {}
            }

        # Operation type breakdown
        operation_stats = {}
        for metric in self.performance_metrics:
            op_type = metric.operation_type.value
            if op_type not in operation_stats:
                operation_stats[op_type] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "total_files_processed": 0,
                    "total_characters_processed": 0,
                    "total_api_calls": 0,
                    "cache_hits": 0,
                    "cache_misses": 0
                }

            stats = operation_stats[op_type]
            stats["count"] += 1
            stats["total_duration_ms"] += metric.duration_ms
            stats["total_files_processed"] += metric.files_processed
            stats["total_characters_processed"] += metric.characters_processed
            stats["total_api_calls"] += metric.api_calls_made
            stats["cache_hits"] += metric.cache_hits
            stats["cache_misses"] += metric.cache_misses

        # Calculate averages
        for op_type, stats in operation_stats.items():
            if stats["count"] > 0:
                stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["count"]
                stats["avg_files_per_operation"] = stats["total_files_processed"] / stats["count"]
                stats["avg_characters_per_operation"] = stats["total_characters_processed"] / stats["count"]

                # Cache efficiency
                total_cache_ops = stats["cache_hits"] + stats["cache_misses"]
                stats["cache_hit_rate"] = (stats["cache_hits"] / total_cache_ops * 100) if total_cache_ops > 0 else 0

        # Overall averages
        total_operations = len(self.performance_metrics)
        avg_duration = sum(m.duration_ms for m in self.performance_metrics) / total_operations if total_operations > 0 else 0

        # Resource usage statistics
        memory_metrics = [m.memory_usage_mb for m in self.performance_metrics if m.memory_usage_mb is not None]
        cpu_metrics = [m.cpu_usage_percent for m in self.performance_metrics if m.cpu_usage_percent is not None]

        resource_usage = {}
        if memory_metrics:
            resource_usage["memory"] = {
                "avg_mb": sum(memory_metrics) / len(memory_metrics),
                "min_mb": min(memory_metrics),
                "max_mb": max(memory_metrics)
            }
        if cpu_metrics:
            resource_usage["cpu"] = {
                "avg_percent": sum(cpu_metrics) / len(cpu_metrics),
                "min_percent": min(cpu_metrics),
                "max_percent": max(cpu_metrics)
            }

        # Efficiency metrics
        total_chars = sum(m.characters_processed for m in self.performance_metrics)
        total_duration = sum(m.duration_ms for m in self.performance_metrics)

        efficiency_metrics = {}
        if total_duration > 0:
            efficiency_metrics["characters_per_second"] = (total_chars / total_duration) * 1000
        if total_operations > 0:
            efficiency_metrics["avg_characters_per_operation"] = total_chars / total_operations

        return {
            "total_operations": total_operations,
            "operation_breakdown": operation_stats,
            "average_metrics": {
                "avg_duration_ms": avg_duration,
                "total_characters_processed": total_chars,
                "total_files_processed": sum(m.files_processed for m in self.performance_metrics)
            },
            "resource_usage": resource_usage,
            "efficiency_metrics": efficiency_metrics
        }

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive metrics report with all statistics."""
        session_duration = (datetime.now(timezone.utc) - self.session_start).total_seconds()

        return {
            "session_info": {
                "session_id": self.session_id,
                "session_start": self.session_start.isoformat(),
                "session_duration_seconds": session_duration,
                "operations_completed": self.operations_completed,
                "operations_failed": self.operations_failed,
                "report_generated_at": datetime.now(timezone.utc).isoformat()
            },
            "api_statistics": self.get_api_statistics(),
            "content_statistics": self.get_content_statistics(),
            "error_statistics": self.get_error_statistics(),
            "performance_statistics": self.get_performance_statistics(),
            "counters": self.counters,
            "gauges": self.gauges,
            "timer_summaries": {
                name: {
                    "count": len(times),
                    "average": sum(times) / len(times) if times else 0,
                    "min": min(times) if times else 0,
                    "max": max(times) if times else 0,
                    "total": sum(times)
                }
                for name, times in self.timers.items()
            },
            "summary": {
                "total_api_calls": len(self.api_metrics),
                "total_content_generations": len(self.content_metrics),
                "total_errors": len(self.error_metrics),
                "total_performance_records": len(self.performance_metrics),
                "overall_success_rate": self._calculate_overall_success_rate()
            }
        }

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall system success rate."""
        total_operations = len(self.api_metrics) + len(self.content_metrics)
        if total_operations == 0:
            return 100.0

        successful_operations = (
            len([m for m in self.api_metrics if m.success]) +
            len([m for m in self.content_metrics if m.success])
        )

        return (successful_operations / total_operations) * 100

    def save_metrics_report(self, output_path: str) -> None:
        """Save comprehensive metrics report to file."""
        report = self.get_comprehensive_report()

        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Metrics report saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save metrics report", error=e)

    def set_github_actions_outputs(self) -> None:
        """Set GitHub Actions output variables with comprehensive metrics."""
        import os

        if not os.getenv("GITHUB_ACTIONS"):
            self.logger.debug("Not in GitHub Actions environment, skipping output setting")
            return

        output_file = os.environ.get("GITHUB_OUTPUT")
        if not output_file:
            self.logger.warning("GITHUB_OUTPUT environment variable not set")
            return

        try:
            api_stats = self.get_api_statistics()
            content_stats = self.get_content_statistics()
            error_stats = self.get_error_statistics()

            # Comprehensive GitHub Actions outputs
            outputs = {
                # API Metrics
                "api_calls_total": api_stats.get("total_calls", 0),
                "api_success_rate": f"{api_stats.get('success_rate', 0):.1f}",
                "api_avg_response_time_ms": f"{api_stats.get('average_response_time_ms', 0):.1f}",
                "tokens_used_total": api_stats.get("total_tokens_used", 0),

                # Content Generation Metrics
                "content_generations_total": content_stats.get("total_generations", 0),
                "content_success_rate": f"{content_stats.get('success_rate', 0):.1f}",
                "tweets_generated_total": content_stats.get("total_tweets_generated", 0),
                "hooks_generated_total": content_stats.get("total_hooks_generated", 0),
                "avg_engagement_score": f"{content_stats.get('average_engagement_score', 0):.2f}",
                "avg_processing_time_ms": f"{content_stats.get('average_processing_time_ms', 0):.1f}",

                # Error Metrics
                "errors_total": error_stats.get("total_errors", 0),
                "error_recovery_rate": f"{error_stats.get('recovery_success_rate', 0):.1f}",

                # Performance Metrics
                "operations_completed": len([m for m in self.content_metrics if m.success]),
                "operations_failed": len([m for m in self.content_metrics if not m.success]),

                # Session Info
                "session_id": self.session_id,
                "session_duration_seconds": f"{(datetime.now(timezone.utc) - self.session_start).total_seconds():.1f}"
            }

            # Add endpoint-specific metrics if available
            if api_stats.get("endpoint_breakdown"):
                for endpoint, stats in api_stats["endpoint_breakdown"].items():
                    safe_endpoint = endpoint.replace("/", "_").replace(".", "_")
                    outputs[f"api_{safe_endpoint}_calls"] = stats.get("calls", 0)
                    outputs[f"api_{safe_endpoint}_success_rate"] = f"{(stats.get('successful', 0) / max(stats.get('calls', 1), 1) * 100):.1f}"

            # Write outputs to GitHub Actions
            with open(output_file, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")

            self.logger.info("GitHub Actions outputs set successfully",
                           outputs_count=len(outputs),
                           **{k: v for k, v in outputs.items() if k in ["api_calls_total", "content_generations_total", "errors_total"]})

        except Exception as e:
            self.logger.error("Failed to set GitHub Actions outputs", error=e)


# Global metrics collector instance
_global_metrics: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _global_metrics

    if _global_metrics is None:
        _global_metrics = MetricsCollector()

    return _global_metrics


def setup_metrics_collection(session_id: Optional[str] = None) -> MetricsCollector:
    """Set up and configure metrics collection."""
    global _global_metrics

    _global_metrics = MetricsCollector(session_id=session_id)

    logger = get_logger()
    logger.info("Metrics collection initialized", session_id=_global_metrics.session_id)

    return _global_metrics