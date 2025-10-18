#!/usr/bin/env python3
"""
Test script for monitoring and metrics collection system.

This script tests the monitoring system components to ensure they work correctly.
"""

import sys
import time
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logger import setup_logging, get_logger, OperationType
from metrics import setup_metrics_collection, ErrorCategory
from monitoring import setup_monitoring, get_health_monitor, get_monitoring_dashboard


def test_metrics_collection():
    """Test basic metrics collection functionality."""
    print("Testing metrics collection...")

    # Set up monitoring
    metrics, health_monitor, dashboard = setup_monitoring("test-session")
    logger = get_logger()

    # Test counter metrics
    metrics.increment_counter("test_counter", 5)
    metrics.increment_counter("test_counter", 3)

    # Test gauge metrics
    metrics.set_gauge("test_gauge", 42.5)

    # Test timer metrics
    with metrics.time_operation("test_operation"):
        time.sleep(0.1)  # Simulate work

    # Test API call recording
    metrics.record_api_call(
        endpoint="https://api.example.com/test",
        method="POST",
        response_time_ms=150.0,
        status_code=200,
        tokens_used=100,
        success=True
    )

    # Test content generation recording
    metrics.record_content_generation(
        operation_type=OperationType.AI_GENERATION,
        post_slug="test-post",
        model_used="test-model",
        input_characters=500,
        output_characters=280,
        processing_time_ms=1000.0,
        tweets_generated=3,
        hooks_generated=2,
        engagement_score=0.85,
        success=True
    )

    # Test error recording
    test_error = Exception("Test error for monitoring")
    metrics.record_error(
        error_category=ErrorCategory.API_ERROR,
        error=test_error,
        operation_type=OperationType.AI_GENERATION,
        post_slug="test-post",
        recovery_attempted=True,
        recovery_successful=False
    )

    # Test performance recording
    metrics.record_performance(
        operation_type=OperationType.CONTENT_DETECTION,
        duration_ms=500.0,
        files_processed=5,
        characters_processed=2500,
        api_calls_made=2,
        cache_hits=3,
        cache_misses=1
    )

    print("✅ Metrics collection test completed")
    return metrics


def test_health_monitoring(metrics):
    """Test health monitoring functionality."""
    print("Testing health monitoring...")

    health_monitor = get_health_monitor()

    # Perform health checks
    system_health = health_monitor.perform_health_checks()

    print(f"Overall system health: {system_health.overall_status.value}")
    print(f"Health checks performed: {len(system_health.checks)}")
    print(f"Active alerts: {len(health_monitor.get_active_alerts())}")

    # Test individual health checks
    api_health = health_monitor.check_api_health()
    print(f"API health: {api_health.status.value} - {api_health.message}")

    content_health = health_monitor.check_content_generation_health()
    print(f"Content generation health: {content_health.status.value} - {content_health.message}")

    error_health = health_monitor.check_error_rate_health()
    print(f"Error rate health: {error_health.status.value} - {error_health.message}")

    resource_health = health_monitor.check_system_resources()
    print(f"System resources health: {resource_health.status.value} - {resource_health.message}")

    print("✅ Health monitoring test completed")
    return health_monitor


def test_dashboard_reporting(metrics):
    """Test dashboard and reporting functionality."""
    print("Testing dashboard reporting...")

    dashboard = get_monitoring_dashboard()

    # Generate dashboard data
    dashboard_data = dashboard.generate_dashboard_data()

    print(f"Dashboard generated at: {dashboard_data['dashboard_generated']}")
    print(f"Session ID: {dashboard_data['metrics_summary']['session_info']['session_id']}")

    # Test statistics
    api_stats = metrics.get_api_statistics()
    print(f"API statistics: {api_stats.get('total_calls', 0)} calls, {api_stats.get('success_rate', 0):.1f}% success rate")

    content_stats = metrics.get_content_statistics()
    print(f"Content statistics: {content_stats.get('total_generations', 0)} generations, {content_stats.get('success_rate', 0):.1f}% success rate")

    error_stats = metrics.get_error_statistics()
    print(f"Error statistics: {error_stats.get('total_errors', 0)} total errors")

    # Test comprehensive report
    comprehensive_report = metrics.get_comprehensive_report()
    print(f"Comprehensive report generated with {len(comprehensive_report)} sections")

    # Test summary report printing
    print("\n" + "="*50)
    print("DASHBOARD SUMMARY REPORT:")
    print("="*50)
    dashboard.print_summary_report()

    print("✅ Dashboard reporting test completed")
    return dashboard


def test_github_actions_integration(metrics):
    """Test GitHub Actions integration."""
    print("Testing GitHub Actions integration...")

    # Test GitHub Actions outputs (will only work in actual GitHub Actions environment)
    try:
        metrics.set_github_actions_outputs()
        print("✅ GitHub Actions outputs set successfully")
    except Exception as e:
        print(f"ℹ️  GitHub Actions outputs not set (not in GitHub Actions environment): {e}")

    print("✅ GitHub Actions integration test completed")


def main():
    """Run all monitoring system tests."""
    print("🧪 Starting monitoring system tests...\n")

    try:
        # Test metrics collection
        metrics = test_metrics_collection()
        print()

        # Test health monitoring
        health_monitor = test_health_monitoring(metrics)
        print()

        # Test dashboard reporting
        dashboard = test_dashboard_reporting(metrics)
        print()

        # Test GitHub Actions integration
        test_github_actions_integration(metrics)
        print()

        # Save test reports
        test_output_dir = Path("test_output")
        test_output_dir.mkdir(exist_ok=True)

        # Save metrics report
        metrics_report_path = test_output_dir / "test-metrics-report.json"
        metrics.save_metrics_report(str(metrics_report_path))
        print(f"📊 Test metrics report saved to: {metrics_report_path}")

        # Save dashboard report
        dashboard_report_path = test_output_dir / "test-dashboard-report.json"
        dashboard.save_dashboard_report(str(dashboard_report_path))
        print(f"📈 Test dashboard report saved to: {dashboard_report_path}")

        print("\n🎉 All monitoring system tests completed successfully!")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())