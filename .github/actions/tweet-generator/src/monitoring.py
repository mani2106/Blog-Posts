"""
Monitoring and performance analysis for the Tweet Thread Generator.

This module provides monitoring dashboards, performance analysis,
alerting capabilities, and health checks for the system.
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from logger import get_logger, OperationType
from metrics import get_metrics_collector, MetricsCollector, ErrorCategory, setup_metrics_collection


class HealthStatus(str, Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Alert:
    """System alert for monitoring and notifications."""
    level: AlertLevel
    title: str
    message: str
    component: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "component": self.component,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved
        }


@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    checks: List[HealthCheck] = field(default_factory=list)
    alerts: List[Alert] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "overall_status": self.overall_status.value,
            "checks": [check.to_dict() for check in self.checks],
            "alerts": [alert.to_dict() for alert in self.alerts],
            "last_updated": self.last_updated.isoformat()
        }


class PerformanceAnalyzer:
    """Analyzes system performance and identifies bottlenecks."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.logger = get_logger()

    def analyze_api_performance(self) -> Dict[str, Any]:
        """Analyze API performance and identify issues."""
        api_stats = self.metrics.get_api_statistics()

        analysis = {
            "status": "healthy",
            "issues": [],
            "recommendations": []
        }

        # Check response times
        avg_response_time = api_stats.get("average_response_time_ms", 0)
        if avg_response_time > 5000:  # 5 seconds
            analysis["status"] = "warning"
            analysis["issues"].append(f"High average response time: {avg_response_time:.1f}ms")
            analysis["recommendations"].append("Consider using faster models or implementing caching")

        # Check success rate
        success_rate = api_stats.get("success_rate", 100)
        if success_rate < 95:
            analysis["status"] = "critical" if success_rate < 80 else "warning"
            analysis["issues"].append(f"Low API success rate: {success_rate:.1f}%")
            analysis["recommendations"].append("Review error logs and implement better retry logic")

        return analysis

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance analysis report."""
        return {
            "api_performance": self.analyze_api_performance(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class HealthMonitor:
    """System health monitoring and alerting."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.logger = get_logger()
        self.performance_analyzer = PerformanceAnalyzer(metrics_collector)
        self.alerts: List[Alert] = []

    def check_api_health(self) -> HealthCheck:
        """Check API connectivity and performance health."""
        try:
            api_stats = self.metrics.get_api_statistics()

            if not api_stats or api_stats.get("total_calls", 0) == 0:
                return HealthCheck(
                    name="api_connectivity",
                    status=HealthStatus.UNKNOWN,
                    message="No API calls recorded yet",
                    details={}
                )

            success_rate = api_stats.get("success_rate", 0)
            avg_response_time = api_stats.get("average_response_time_ms", 0)

            if success_rate >= 95 and avg_response_time < 5000:
                status = HealthStatus.HEALTHY
                message = f"API healthy: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg response"
            elif success_rate >= 80 and avg_response_time < 10000:
                status = HealthStatus.WARNING
                message = f"API degraded: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg response"
            else:
                status = HealthStatus.CRITICAL
                message = f"API critical: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg response"

            return HealthCheck(
                name="api_connectivity",
                status=status,
                message=message,
                details={
                    "success_rate": success_rate,
                    "average_response_time_ms": avg_response_time,
                    "total_calls": api_stats.get("total_calls", 0),
                    "total_tokens_used": api_stats.get("total_tokens_used", 0)
                }
            )

        except Exception as e:
            self.logger.error("Failed to check API health", error=e)
            return HealthCheck(
                name="api_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_content_generation_health(self) -> HealthCheck:
        """Check content generation system health."""
        try:
            content_stats = self.metrics.get_content_statistics()

            if not content_stats or content_stats.get("total_generations", 0) == 0:
                return HealthCheck(
                    name="content_generation",
                    status=HealthStatus.UNKNOWN,
                    message="No content generation recorded yet",
                    details={}
                )

            success_rate = content_stats.get("success_rate", 0)
            avg_engagement = content_stats.get("average_engagement_score", 0)

            if success_rate >= 90 and avg_engagement >= 0.7:
                status = HealthStatus.HEALTHY
                message = f"Content generation healthy: {success_rate:.1f}% success, {avg_engagement:.2f} avg engagement"
            elif success_rate >= 70 and avg_engagement >= 0.5:
                status = HealthStatus.WARNING
                message = f"Content generation degraded: {success_rate:.1f}% success, {avg_engagement:.2f} avg engagement"
            else:
                status = HealthStatus.CRITICAL
                message = f"Content generation critical: {success_rate:.1f}% success, {avg_engagement:.2f} avg engagement"

            return HealthCheck(
                name="content_generation",
                status=status,
                message=message,
                details={
                    "success_rate": success_rate,
                    "average_engagement_score": avg_engagement,
                    "total_generations": content_stats.get("total_generations", 0),
                    "tweets_generated": content_stats.get("total_tweets_generated", 0)
                }
            )

        except Exception as e:
            self.logger.error("Failed to check content generation health", error=e)
            return HealthCheck(
                name="content_generation",
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_error_rate_health(self) -> HealthCheck:
        """Check system error rate health."""
        try:
            error_stats = self.metrics.get_error_statistics()
            total_errors = error_stats.get("total_errors", 0)

            # Calculate error rate based on total operations
            total_operations = (
                self.metrics.get_api_statistics().get("total_calls", 0) +
                self.metrics.get_content_statistics().get("total_generations", 0)
            )

            if total_operations == 0:
                return HealthCheck(
                    name="error_rate",
                    status=HealthStatus.UNKNOWN,
                    message="No operations recorded yet",
                    details={}
                )

            error_rate = (total_errors / total_operations) * 100

            if error_rate <= 5:
                status = HealthStatus.HEALTHY
                message = f"Low error rate: {error_rate:.1f}% ({total_errors}/{total_operations})"
            elif error_rate <= 15:
                status = HealthStatus.WARNING
                message = f"Moderate error rate: {error_rate:.1f}% ({total_errors}/{total_operations})"
            else:
                status = HealthStatus.CRITICAL
                message = f"High error rate: {error_rate:.1f}% ({total_errors}/{total_operations})"

            return HealthCheck(
                name="error_rate",
                status=status,
                message=message,
                details={
                    "error_rate_percent": error_rate,
                    "total_errors": total_errors,
                    "total_operations": total_operations,
                    "category_breakdown": error_stats.get("category_breakdown", {})
                }
            )

        except Exception as e:
            self.logger.error("Failed to check error rate health", error=e)
            return HealthCheck(
                name="error_rate",
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_system_resources(self) -> HealthCheck:
        """Check system resource usage."""
        try:
            import psutil
            import os

            # Get memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # Get CPU usage
            cpu_percent = process.cpu_percent()

            # Determine status based on resource usage
            if memory_mb < 500 and cpu_percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Resources healthy: {memory_mb:.1f}MB memory, {cpu_percent:.1f}% CPU"
            elif memory_mb < 1000 and cpu_percent < 90:
                status = HealthStatus.WARNING
                message = f"Resources elevated: {memory_mb:.1f}MB memory, {cpu_percent:.1f}% CPU"
            else:
                status = HealthStatus.CRITICAL
                message = f"Resources critical: {memory_mb:.1f}MB memory, {cpu_percent:.1f}% CPU"

            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                details={
                    "memory_mb": memory_mb,
                    "cpu_percent": cpu_percent,
                    "process_id": os.getpid()
                }
            )

        except ImportError:
            # psutil not available
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message="Resource monitoring not available (psutil not installed)",
                details={}
            )
        except Exception as e:
            self.logger.error("Failed to check system resources", error=e)
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.WARNING,
                message=f"Resource check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_performance_health(self) -> HealthCheck:
        """Check system performance health."""
        try:
            perf_stats = self.metrics.get_performance_statistics()

            if not perf_stats or perf_stats.get("total_operations", 0) == 0:
                return HealthCheck(
                    name="performance",
                    status=HealthStatus.UNKNOWN,
                    message="No performance data recorded yet",
                    details={}
                )

            avg_duration = perf_stats.get("average_metrics", {}).get("avg_duration_ms", 0)
            resource_usage = perf_stats.get("resource_usage", {})

            # Check memory usage if available
            memory_status = HealthStatus.HEALTHY
            memory_msg = "Memory usage normal"
            if "memory" in resource_usage:
                avg_memory = resource_usage["memory"]["avg_mb"]
                if avg_memory > 1000:  # 1GB
                    memory_status = HealthStatus.CRITICAL
                    memory_msg = f"High memory usage: {avg_memory:.1f}MB"
                elif avg_memory > 500:  # 500MB
                    memory_status = HealthStatus.WARNING
                    memory_msg = f"Elevated memory usage: {avg_memory:.1f}MB"

            # Check processing speed
            speed_status = HealthStatus.HEALTHY
            speed_msg = "Processing speed normal"
            if avg_duration > 30000:  # 30 seconds
                speed_status = HealthStatus.WARNING
                speed_msg = f"Slow processing: {avg_duration:.1f}ms average"
            elif avg_duration > 60000:  # 60 seconds
                speed_status = HealthStatus.CRITICAL
                speed_msg = f"Very slow processing: {avg_duration:.1f}ms average"

            # Determine overall performance status
            if memory_status == HealthStatus.CRITICAL or speed_status == HealthStatus.CRITICAL:
                status = HealthStatus.CRITICAL
                message = f"Performance critical: {memory_msg}, {speed_msg}"
            elif memory_status == HealthStatus.WARNING or speed_status == HealthStatus.WARNING:
                status = HealthStatus.WARNING
                message = f"Performance degraded: {memory_msg}, {speed_msg}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Performance healthy: {avg_duration:.1f}ms avg processing"

            return HealthCheck(
                name="performance",
                status=status,
                message=message,
                details={
                    "avg_duration_ms": avg_duration,
                    "total_operations": perf_stats.get("total_operations", 0),
                    "memory_usage": resource_usage.get("memory", {}),
                    "cpu_usage": resource_usage.get("cpu", {}),
                    "efficiency_metrics": perf_stats.get("efficiency_metrics", {})
                }
            )

        except Exception as e:
            self.logger.error("Failed to check performance health", error=e)
            return HealthCheck(
                name="performance",
                status=HealthStatus.CRITICAL,
                message=f"Performance check failed: {str(e)}",
                details={"error": str(e)}
            )

    def perform_health_checks(self) -> SystemHealth:
        """Perform comprehensive health checks and return system health status."""
        checks = [
            self.check_api_health(),
            self.check_content_generation_health(),
            self.check_error_rate_health(),
            self.check_system_resources(),
            self.check_performance_health()
        ]

        # Determine overall status
        statuses = [check.status for check in checks]
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif HealthStatus.UNKNOWN in statuses:
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY

        # Generate alerts for critical and warning conditions
        new_alerts = []
        for check in checks:
            if check.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                alert = Alert(
                    level=AlertLevel.CRITICAL if check.status == HealthStatus.CRITICAL else AlertLevel.WARNING,
                    title=f"{check.name.replace('_', ' ').title()} Issue",
                    message=check.message,
                    component=check.name,
                    details=check.details
                )
                new_alerts.append(alert)

        self.alerts.extend(new_alerts)

        return SystemHealth(
            overall_status=overall_status,
            checks=checks,
            alerts=self.alerts
        )

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]


class MonitoringDashboard:
    """Monitoring dashboard for system overview and reporting."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.health_monitor = HealthMonitor(metrics_collector)
        self.performance_analyzer = PerformanceAnalyzer(metrics_collector)
        self.logger = get_logger()

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data with all metrics."""
        system_health = self.health_monitor.perform_health_checks()
        performance_report = self.performance_analyzer.get_performance_report()
        metrics_report = self.metrics.get_comprehensive_report()

        return {
            "dashboard_generated": datetime.now(timezone.utc).isoformat(),
            "system_health": system_health.to_dict(),
            "performance_analysis": performance_report,
            "metrics_summary": {
                "session_info": metrics_report["session_info"],
                "api_statistics": metrics_report["api_statistics"],
                "content_statistics": metrics_report["content_statistics"],
                "error_statistics": metrics_report["error_statistics"],
                "performance_statistics": metrics_report["performance_statistics"]
            },
            "key_metrics": {
                "total_api_calls": metrics_report["counters"].get("api_calls_total", 0),
                "api_success_rate": metrics_report["api_statistics"].get("success_rate", 0),
                "api_avg_response_time": metrics_report["api_statistics"].get("average_response_time_ms", 0),
                "content_generations": metrics_report["counters"].get("content_generation_total", 0),
                "content_success_rate": metrics_report["content_statistics"].get("success_rate", 0),
                "tweets_generated": metrics_report["counters"].get("tweets_generated_total", 0),
                "hooks_generated": metrics_report["counters"].get("hooks_generated_total", 0),
                "avg_engagement_score": metrics_report["content_statistics"].get("average_engagement_score", 0),
                "total_errors": metrics_report["counters"].get("errors_total", 0),
                "error_recovery_rate": metrics_report["error_statistics"].get("recovery_success_rate", 0),
                "tokens_used": metrics_report["counters"].get("tokens_used_total", 0),
                "overall_success_rate": metrics_report["summary"].get("overall_success_rate", 0)
            },
            "performance_summary": {
                "total_operations": metrics_report["performance_statistics"].get("total_operations", 0),
                "avg_processing_time": metrics_report["performance_statistics"].get("average_metrics", {}).get("avg_duration_ms", 0),
                "characters_per_second": metrics_report["performance_statistics"].get("efficiency_metrics", {}).get("characters_per_second", 0),
                "memory_usage": metrics_report["performance_statistics"].get("resource_usage", {}).get("memory", {}),
                "cpu_usage": metrics_report["performance_statistics"].get("resource_usage", {}).get("cpu", {})
            }
        }

    def save_dashboard_report(self, output_path: str) -> None:
        """Save dashboard report to file."""
        try:
            dashboard_data = self.generate_dashboard_data()

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, default=str)

            self.logger.info(f"Dashboard report saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save dashboard report", error=e)

    def print_summary_report(self) -> None:
        """Print a comprehensive summary report to console/logs."""
        try:
            dashboard_data = self.generate_dashboard_data()

            print("\n" + "="*70)
            print("TWEET THREAD GENERATOR - COMPREHENSIVE MONITORING SUMMARY")
            print("="*70)

            # System Health
            health = dashboard_data["system_health"]
            print(f"\nSYSTEM HEALTH: {health['overall_status'].upper()}")

            for check in health["checks"]:
                status_icon = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "critical": "❌",
                    "unknown": "❓"
                }.get(check["status"], "❓")
                print(f"  {status_icon} {check['name'].replace('_', ' ').title()}: {check['message']}")

            # Key Metrics
            metrics = dashboard_data["key_metrics"]
            print(f"\nAPI METRICS:")
            print(f"  📊 Total Calls: {metrics['total_api_calls']} (Success Rate: {metrics['api_success_rate']:.1f}%)")
            print(f"  ⏱️  Avg Response Time: {metrics['api_avg_response_time']:.1f}ms")
            print(f"  🪙 Tokens Used: {metrics['tokens_used']:,}")

            print(f"\nCONTENT METRICS:")
            print(f"  📝 Content Generated: {metrics['content_generations']} posts (Success Rate: {metrics['content_success_rate']:.1f}%)")
            print(f"  🐦 Tweets Generated: {metrics['tweets_generated']}")
            print(f"  🎯 Hooks Generated: {metrics['hooks_generated']}")
            print(f"  📈 Avg Engagement Score: {metrics['avg_engagement_score']:.2f}")

            print(f"\nERROR METRICS:")
            print(f"  ❌ Total Errors: {metrics['total_errors']}")
            print(f"  🔄 Error Recovery Rate: {metrics['error_recovery_rate']:.1f}%")
            print(f"  ✅ Overall Success Rate: {metrics['overall_success_rate']:.1f}%")

            # Performance Summary
            perf = dashboard_data["performance_summary"]
            print(f"\nPERFORMANCE METRICS:")
            print(f"  ⚡ Total Operations: {perf['total_operations']}")
            print(f"  ⏱️  Avg Processing Time: {perf['avg_processing_time']:.1f}ms")
            if perf['characters_per_second'] > 0:
                print(f"  📊 Processing Speed: {perf['characters_per_second']:.1f} chars/sec")

            # Resource usage
            if perf['memory_usage']:
                memory = perf['memory_usage']
                print(f"  💾 Memory Usage: {memory.get('avg_mb', 0):.1f}MB avg (max: {memory.get('max_mb', 0):.1f}MB)")

            if perf['cpu_usage']:
                cpu = perf['cpu_usage']
                print(f"  🖥️  CPU Usage: {cpu.get('avg_percent', 0):.1f}% avg (max: {cpu.get('max_percent', 0):.1f}%)")

            # Active Alerts
            active_alerts = [alert for alert in health["alerts"] if not alert.get("resolved", False)]
            if active_alerts:
                print(f"\nACTIVE ALERTS ({len(active_alerts)}):")
                for alert in active_alerts:
                    level_icon = {
                        "info": "ℹ️",
                        "warning": "⚠️",
                        "error": "❌",
                        "critical": "🚨"
                    }.get(alert["level"], "❓")
                    print(f"  {level_icon} {alert['title']}: {alert['message']}")
            else:
                print(f"\n✅ NO ACTIVE ALERTS")

            # Session Info
            session = dashboard_data["metrics_summary"]["session_info"]
            print(f"\nSESSION INFO:")
            print(f"  🆔 Session ID: {session['session_id']}")
            print(f"  ⏰ Duration: {session['session_duration_seconds']:.1f}s")
            print(f"  📊 Operations: {session['operations_completed']} completed, {session['operations_failed']} failed")

            print("="*70)

        except Exception as e:
            self.logger.error("Failed to print summary report", error=e)


# Global monitoring instances
_global_health_monitor: Optional[HealthMonitor] = None
_global_dashboard: Optional[MonitoringDashboard] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create global health monitor instance."""
    global _global_health_monitor

    if _global_health_monitor is None:
        metrics = get_metrics_collector()
        _global_health_monitor = HealthMonitor(metrics)

    return _global_health_monitor


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get or create global monitoring dashboard instance."""
    global _global_dashboard

    if _global_dashboard is None:
        metrics = get_metrics_collector()
        _global_dashboard = MonitoringDashboard(metrics)

    return _global_dashboard


def setup_monitoring(session_id: Optional[str] = None) -> Tuple[MetricsCollector, HealthMonitor, MonitoringDashboard]:
    """Set up complete monitoring system."""
    global _global_health_monitor, _global_dashboard

    # Set up metrics collection
    metrics = setup_metrics_collection(session_id)

    # Set up health monitoring
    _global_health_monitor = HealthMonitor(metrics)

    # Set up dashboard
    _global_dashboard = MonitoringDashboard(metrics)

    logger = get_logger()
    logger.info("Monitoring system initialized",
               session_id=metrics.session_id,
               components=["metrics", "health_monitor", "dashboard"])

    return metrics, _global_health_monitor, _global_dashboard
# """
# import json
# import time
# from datetime import datetime, timezone
# from typing import Dict, Any, List, Optional, Tuple
# from pathlib import Path
# from dataclasses import dataclass, field
# from enum import Enum

# from logger import get_logger, OperationType
# from metrics import get_metrics_collector, MetricsCollector, ErrorCategory, setup_metrics_collection


# class HealthStatus(str, Enum):
#     """System health status levels."""
#     HEALTHY = "healthy"
#     WARNING = "warning"
#     CRITICAL = "critical"
#     UNKNOWN = "unknown"


# @dataclass
# class HealthCheck:
#     """Individual health check result."""
#     name: str
#     status: HealthStatus
#     message: str
#     details: Dict[str, Any] = field(default_factory=dict)
#     timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

#     def to_dict(self) -> Dict[str, Any]:
#         """Convert to dictionary for serialization."""
#         return {
#             "name": self.name,
#             "status": self.status.value,
#             "message": self.message,
#             "details": self.details,
#             "timestamp": self.timestamp.isoformat()
#         }


# class HealthMonitor:
#     """System health monitoring and alerting."""

#     def __init__(self, metrics_collector: MetricsCollector):
#         self.metrics = metrics_collector
#         self.logger = get_logger()

#     def check_api_health(self) -> HealthCheck:
#         """Check API connectivity and performance health."""
#         try:
#             api_stats = self.metrics.get_api_statistics()

#             if not api_stats or api_stats.get("total_calls", 0) == 0:
#                 return HealthCheck(
#                     name="api_connectivity",
#                     status=HealthStatus.UNKNOWN,
#                     message="No API calls recorded yet",
#                     details={}
#                 )

#             success_rate = api_stats.get("success_rate", 0)
#             avg_response_time = api_stats.get("average_response_time_ms", 0)

#             if success_rate >= 95 and avg_response_time < 5000:
#                 status = HealthStatus.HEALTHY
#                 message = f"API healthy: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg response"
#             elif success_rate >= 80 and avg_response_time < 10000:
#                 status = HealthStatus.WARNING
#                 message = f"API degraded: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg response"
#             else:
#                 status = HealthStatus.CRITICAL
#                 message = f"API critical: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg response"

#             return HealthCheck(
#                 name="api_connectivity",
#                 status=status,
#                 message=message,
#                 details={
#                     "success_rate": success_rate,
#                     "average_response_time_ms": avg_response_time,
#                     "total_calls": api_stats.get("total_calls", 0),
#                     "total_tokens_used": api_stats.get("total_tokens_used", 0)
#                 }
#             )

#         except Exception as e:
#             self.logger.error("Failed to check API health", error=e)
#             return HealthCheck(
#                 name="api_connectivity",
#                 status=HealthStatus.CRITICAL,
#                 message=f"Health check failed: {str(e)}",
#                 details={"error": str(e)}
#             )

#     def perform_health_checks(self) -> List[HealthCheck]:
#         """Perform all health checks and return results."""
#         return [self.check_api_health()]


# class MonitoringDashboard:
#     """Monitoring dashboard for system overview and reporting."""

#     def __init__(self, metrics_collector: MetricsCollector):
#         self.metrics = metrics_collector
#         self.health_monitor = HealthMonitor(metrics_collector)
#         self.logger = get_logger()

#     def generate_dashboard_data(self) -> Dict[str, Any]:
#         """Generate comprehensive dashboard data."""
#         health_checks = self.health_monitor.perform_health_checks()
#         metrics_report = self.metrics.get_comprehensive_report()

#         return {
#             "dashboard_generated": datetime.now(timezone.utc).isoformat(),
#             "health_checks": [check.to_dict() for check in health_checks],
#             "metrics_summary": {
#                 "session_info": metrics_report["session_info"],
#                 "api_statistics": metrics_report["api_statistics"],
#                 "content_statistics": metrics_report["content_statistics"],
#                 "error_statistics": metrics_report["error_statistics"]
#             },
#             "key_metrics": {
#                 "total_api_calls": metrics_report["counters"].get("api_calls_total", 0),
#                 "api_success_rate": metrics_report["api_statistics"].get("success_rate", 0),
#                 "content_generations": metrics_report["counters"].get("content_generation_total", 0),
#                 "tweets_generated": metrics_report["counters"].get("tweets_generated_total", 0),
#                 "total_errors": metrics_report["counters"].get("errors_total", 0),
#                 "tokens_used": metrics_report["counters"].get("tokens_used_total", 0)
#             }
#         }

#     def print_summary_report(self) -> None:
#         """Print a summary report to console/logs."""
#         try:
#             dashboard_data = self.generate_dashboard_data()

#             print("\n" + "="*60)
#             print("TWEET THREAD GENERATOR - MONITORING SUMMARY")
#             print("="*60)

#             # Health Checks
#             health_checks = dashboard_data["health_checks"]
#             print(f"\nHEALTH CHECKS:")
#             for check in health_checks:
#                 status_icon = {
#                     "healthy": "✅",
#                     "warning": "⚠️",
#                     "critical": "❌",
#                     "unknown": "❓"
#                 }.get(check["status"], "❓")
#                 print(f"  {status_icon} {check['name'].replace('_', ' ').title()}: {check['message']}")

#             # Key Metrics
#             metrics = dashboard_data["key_metrics"]
#             print(f"\nKEY METRICS:")
#             print(f"  📊 API Calls: {metrics['total_api_calls']} (Success Rate: {metrics['api_success_rate']:.1f}%)")
#             print(f"  📝 Content Generated: {metrics['content_generations']} posts")
#             print(f"  🐦 Tweets Generated: {metrics['tweets_generated']}")
#             print(f"  🪙 Tokens Used: {metrics['tokens_used']:,}")
#             print(f"  ❌ Total Errors: {metrics['total_errors']}")

#             print("="*60)

#         except Exception as e:
#             self.logger.error("Failed to print summary report", error=e)


# # Global monitoring instances
# _global_health_monitor: Optional[HealthMonitor] = None
# _global_dashboard: Optional[MonitoringDashboard] = None


# def get_health_monitor() -> HealthMonitor:
#     """Get or create global health monitor instance."""
#     global _global_health_monitor

#     if _global_health_monitor is None:
#         metrics = get_metrics_collector()
#         _global_health_monitor = HealthMonitor(metrics)

#     return _global_health_monitor


# def get_monitoring_dashboard() -> MonitoringDashboard:
#     """Get or create global monitoring dashboard instance."""
#     global _global_dashboard

#     if _global_dashboard is None:
#         metrics = get_metrics_collector()
#         _global_dashboard = MonitoringDashboard(metrics)

#     return _global_dashboard


# def setup_monitoring(session_id: Optional[str] = None) -> Tuple[MetricsCollector, HealthMonitor, MonitoringDashboard]:
#     """Set up complete monitoring system."""
#     global _global_health_monitor, _global_dashboard

#     # Set up metrics collection
#     metrics = setup_metrics_collection(session_id)

#     # Set up health monitoring
#     _global_health_monitor = HealthMonitor(metrics)

#     # Set up dashboard
#     _global_dashboard = MonitoringDashboard(metrics)

#     logger = get_logger()
#     logger.info("Monitoring system initialized",
#                session_id=metrics.session_id,
#                components=["metrics", "health_monitor", "dashboard"])

#     return metrics, _global_health_monitor, _global_dashboard