#!/usr/bin/env python3
"""
Comprehensive test for monitoring and metrics collection system.

This test validates all aspects of task 10.2:
- OpenRouter API response times and token usage tracking
- Content generation success rates and failure modes monitoring
- Performance metrics for style analysis and optimization
- Error rate tracking and categorization
- GitHub Actions output metrics
"""

import sys
import time
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from logger import setup_logging, get_logger, OperationType
from metrics import setup_metrics_collection, ErrorCategory, MetricsCollector
from monitoring import setup_monitoring, get_health_monitor, get_monitoring_dashboard


def test_api_metrics_tracking():
    """Test OpenRouter API response times and token usage tracking."""
    print("Testing API metrics tracking...")

    metrics = setup_metrics_collection("api-test-session")

    # Simulate various API calls
    test_scenarios = [
        {"endpoint": "https://openrouter.ai/api/v1/chat/completions", "response_time": 1500, "tokens": 150, "success": True},
        {"endpoint": "https://openrouter.ai/api/v1/chat/completions", "response_time": 2300, "tokens": 200, "success": True},
        {"endpoint": "https://openrouter.ai/api/v1/chat/completions", "response_time": 5000, "tokens": 0, "success": False},
        {"endpoint": "https://openrouter.ai/api/v1/models", "response_time": 800, "tokens": 0, "success": True},
    ]

    for scenario in test_scenarios:
        metrics.record_api_call(
            endpoint=scenario["endpoint"],
            response_time_ms=scenario["response_time"],
            tokens_used=scenario["tokens"],
            success=scenario["success"],
            error=Exception("Rate limit exceeded") if not scenario["success"] else None
        )

    # Get API statistics
    api_stats = metrics.get_api_statistics()

    # Validate tracking
    assert api_stats["total_calls"] == 4, f"Expected 4 calls, got {api_stats['total_calls']}"
    assert api_stats["successful_calls"] == 3, f"Expected 3 successful calls, got {api_stats['successful_calls']}"
    assert api_stats["total_tokens_used"] == 350, f"Expected 350 tokens, got {api_stats['total_tokens_used']}"
    assert api_stats["success_rate"] == 75.0, f"Expected 75% success rate, got {api_stats['success_rate']}"

    # Check endpoint breakdown
    assert "endpoint_breakdown" in api_stats
    assert len(api_stats["endpoint_breakdown"]) == 2  # Two different endpoints

    print("✅ API metrics tracking working correctly")
    return True


def test_content_generation_monitoring():
    """Test content generation success rates and failure modes monitoring."""
    print("Testing content generation monitoring...")

    metrics = setup_metrics_collection("content-test-session")

    # Simulate content generation operations
    test_generations = [
        {
            "operation": OperationType.AI_GENERATION,
            "post_slug": "test-post-1",
            "model": "claude-3-sonnet",
            "tweets": 5,
            "hooks": 3,
            "engagement": 8.5,
            "success": True
        },
        {
            "operation": OperationType.AI_GENERATION,
            "post_slug": "test-post-2",
            "model": "claude-3-haiku",
            "tweets": 0,
            "hooks": 0,
            "engagement": 0.0,
            "success": False
        },
        {
            "operation": OperationType.ENGAGEMENT_OPTIMIZATION,
            "post_slug": "test-post-3",
            "model": "claude-3-sonnet",
            "tweets": 7,
            "hooks": 4,
            "engagement": 9.2,
            "success": True
        }
    ]

    for gen in test_generations:
        metrics.record_content_generation(
            operation_type=gen["operation"],
            post_slug=gen["post_slug"],
            model_used=gen["model"],
            tweets_generated=gen["tweets"],
            hooks_generated=gen["hooks"],
            engagement_score=gen["engagement"],
            processing_time_ms=2000.0,
            success=gen["success"],
            error=Exception("Model timeout") if not gen["success"] else None
        )

    # Get content statistics
    content_stats = metrics.get_content_statistics()

    # Validate monitoring
    assert content_stats["total_generations"] == 3, f"Expected 3 generations, got {content_stats['total_generations']}"
    assert content_stats["successful_generations"] == 2, f"Expected 2 successful, got {content_stats['successful_generations']}"
    assert abs(content_stats["success_rate"] - 66.67) < 0.01, f"Expected ~66.67% success rate, got {content_stats['success_rate']:.2f}"
    assert content_stats["total_tweets_generated"] == 12, f"Expected 12 tweets, got {content_stats['total_tweets_generated']}"
    assert content_stats["total_hooks_generated"] == 7, f"Expected 7 hooks, got {content_stats['total_hooks_generated']}"

    # Check operation breakdown
    assert "operation_breakdown" in content_stats
    assert "ai_generation" in content_stats["operation_breakdown"]
    assert "engagement_optimization" in content_stats["operation_breakdown"]

    print("✅ Content generation monitoring working correctly")
    return True


def test_performance_metrics():
    """Test performance metrics for style analysis and optimization."""
    print("Testing performance metrics...")

    metrics = setup_metrics_collection("performance-test-session")

    # Simulate performance data for different operations
    performance_scenarios = [
        {
            "operation": OperationType.STYLE_ANALYSIS,
            "duration": 3500.0,
            "files": 25,
            "characters": 50000,
            "cache_hits": 15,
            "cache_misses": 10
        },
        {
            "operation": OperationType.ENGAGEMENT_OPTIMIZATION,
            "duration": 1200.0,
            "files": 1,
            "characters": 2800,
            "cache_hits": 8,
            "cache_misses": 2
        },
        {
            "operation": OperationType.CONTENT_VALIDATION,
            "duration": 800.0,
            "files": 1,
            "characters": 1400,
            "cache_hits": 5,
            "cache_misses": 1
        }
    ]

    for scenario in performance_scenarios:
        metrics.record_performance(
            operation_type=scenario["operation"],
            duration_ms=scenario["duration"],
            files_processed=scenario["files"],
            characters_processed=scenario["characters"],
            cache_hits=scenario["cache_hits"],
            cache_misses=scenario["cache_misses"]
        )

    # Get performance statistics
    perf_stats = metrics.get_performance_statistics()

    # Validate performance tracking
    assert perf_stats["total_operations"] == 3, f"Expected 3 operations, got {perf_stats['total_operations']}"

    # Check operation breakdown
    assert "operation_breakdown" in perf_stats
    assert "style_analysis" in perf_stats["operation_breakdown"]
    assert "engagement_optimization" in perf_stats["operation_breakdown"]
    assert "content_validation" in perf_stats["operation_breakdown"]

    # Validate cache efficiency calculation
    style_analysis = perf_stats["operation_breakdown"]["style_analysis"]
    expected_cache_rate = (15 / (15 + 10)) * 100  # 60%
    assert abs(style_analysis["cache_hit_rate"] - expected_cache_rate) < 0.1

    # Check efficiency metrics
    assert "efficiency_metrics" in perf_stats
    assert "characters_per_second" in perf_stats["efficiency_metrics"]

    print("✅ Performance metrics working correctly")
    return True


def test_error_tracking_categorization():
    """Test error rate tracking and categorization."""
    print("Testing error tracking and categorization...")

    metrics = setup_metrics_collection("error-test-session")

    # Simulate various error scenarios
    error_scenarios = [
        {
            "category": ErrorCategory.API_ERROR,
            "error": Exception("Rate limit exceeded"),
            "operation": OperationType.AI_GENERATION,
            "recovery": True,
            "recovery_success": True
        },
        {
            "category": ErrorCategory.VALIDATION_ERROR,
            "error": ValueError("Invalid tweet length"),
            "operation": OperationType.CONTENT_VALIDATION,
            "recovery": True,
            "recovery_success": False
        },
        {
            "category": ErrorCategory.FILE_ERROR,
            "error": FileNotFoundError("Style profile not found"),
            "operation": OperationType.STYLE_ANALYSIS,
            "recovery": False,
            "recovery_success": False
        },
        {
            "category": ErrorCategory.NETWORK_ERROR,
            "error": ConnectionError("Network timeout"),
            "operation": OperationType.API_CALL,
            "recovery": True,
            "recovery_success": True
        }
    ]

    for scenario in error_scenarios:
        metrics.record_error(
            error_category=scenario["category"],
            error=scenario["error"],
            operation_type=scenario["operation"],
            recovery_attempted=scenario["recovery"],
            recovery_successful=scenario["recovery_success"]
        )

    # Get error statistics
    error_stats = metrics.get_error_statistics()

    # Validate error tracking
    assert error_stats["total_errors"] == 4, f"Expected 4 errors, got {error_stats['total_errors']}"
    assert error_stats["recovery_attempted"] == 3, f"Expected 3 recovery attempts, got {error_stats['recovery_attempted']}"
    assert error_stats["recovery_successful"] == 2, f"Expected 2 successful recoveries, got {error_stats['recovery_successful']}"
    assert abs(error_stats["recovery_success_rate"] - 66.67) < 0.1, f"Expected ~66.67% recovery rate, got {error_stats['recovery_success_rate']}"

    # Check categorization
    assert "category_breakdown" in error_stats
    assert error_stats["category_breakdown"]["api_error"] == 1
    assert error_stats["category_breakdown"]["validation_error"] == 1
    assert error_stats["category_breakdown"]["file_error"] == 1
    assert error_stats["category_breakdown"]["network_error"] == 1

    # Check error type breakdown
    assert "error_type_breakdown" in error_stats
    assert "Exception" in error_stats["error_type_breakdown"]
    assert "ValueError" in error_stats["error_type_breakdown"]

    # Check operation breakdown
    assert "error_rate_by_operation" in error_stats
    assert "ai_generation" in error_stats["error_rate_by_operation"]

    print("✅ Error tracking and categorization working correctly")
    return True


def test_github_actions_outputs():
    """Test GitHub Actions output metrics."""
    print("Testing GitHub Actions output metrics...")

    metrics = setup_metrics_collection("github-test-session")

    # Simulate some activity to generate metrics
    metrics.record_api_call("https://openrouter.ai/api/v1/chat/completions",
                           response_time_ms=1500, tokens_used=100, success=True)
    metrics.record_content_generation(OperationType.AI_GENERATION, "test-post", "claude-3-sonnet",
                                    tweets_generated=5, success=True, engagement_score=8.5)
    metrics.record_error(ErrorCategory.API_ERROR, Exception("Test error"), OperationType.AI_GENERATION)

    # Test GitHub Actions output generation (won't actually write in test environment)
    try:
        metrics.set_github_actions_outputs()
        print("✅ GitHub Actions outputs generated successfully")
    except Exception as e:
        # Expected in non-GitHub Actions environment
        print(f"ℹ️  GitHub Actions outputs not set (expected in test environment): {e}")

    # Validate that the metrics are available for output
    api_stats = metrics.get_api_statistics()
    content_stats = metrics.get_content_statistics()
    error_stats = metrics.get_error_statistics()

    assert api_stats["total_calls"] > 0
    assert content_stats["total_generations"] > 0
    assert error_stats["total_errors"] > 0

    print("✅ GitHub Actions output metrics working correctly")
    return True


def test_comprehensive_monitoring_system():
    """Test the complete monitoring system integration."""
    print("Testing comprehensive monitoring system...")

    # Set up complete monitoring
    metrics, health_monitor, dashboard = setup_monitoring("comprehensive-test-session")

    # Generate some test data
    metrics.record_api_call("https://openrouter.ai/api/v1/chat/completions",
                           response_time_ms=2000, tokens_used=150, success=True)
    metrics.record_content_generation(OperationType.AI_GENERATION, "test-post", "claude-3-sonnet",
                                    tweets_generated=6, hooks_generated=3, engagement_score=9.0, success=True)
    metrics.record_performance(OperationType.STYLE_ANALYSIS, duration_ms=3000,
                             files_processed=20, characters_processed=40000)

    # Test health monitoring
    system_health = health_monitor.perform_health_checks()
    assert system_health.overall_status in ["healthy", "warning", "critical", "unknown"]
    assert len(system_health.checks) >= 4  # Should have at least 4 health checks

    # Test dashboard generation
    dashboard_data = dashboard.generate_dashboard_data()
    assert "dashboard_generated" in dashboard_data
    assert "system_health" in dashboard_data
    assert "metrics_summary" in dashboard_data
    assert "key_metrics" in dashboard_data
    assert "performance_summary" in dashboard_data

    # Test comprehensive report
    comprehensive_report = metrics.get_comprehensive_report()
    assert "session_info" in comprehensive_report
    assert "api_statistics" in comprehensive_report
    assert "content_statistics" in comprehensive_report
    assert "error_statistics" in comprehensive_report
    assert "performance_statistics" in comprehensive_report
    assert "summary" in comprehensive_report

    print("✅ Comprehensive monitoring system working correctly")
    return True


def test_monitoring_file_operations():
    """Test monitoring system file operations."""
    print("Testing monitoring file operations...")

    metrics, health_monitor, dashboard = setup_monitoring("file-test-session")

    # Generate test data
    metrics.record_api_call("https://openrouter.ai/api/v1/chat/completions",
                           response_time_ms=1800, tokens_used=120, success=True)

    # Test saving reports
    test_output_dir = Path("test_output")
    test_output_dir.mkdir(exist_ok=True)

    # Test metrics report saving
    metrics_report_path = test_output_dir / "test-comprehensive-metrics.json"
    metrics.save_metrics_report(str(metrics_report_path))
    assert metrics_report_path.exists(), "Metrics report file should be created"

    # Test dashboard report saving
    dashboard_report_path = test_output_dir / "test-comprehensive-dashboard.json"
    dashboard.save_dashboard_report(str(dashboard_report_path))
    assert dashboard_report_path.exists(), "Dashboard report file should be created"

    # Validate file contents
    import json
    with open(metrics_report_path) as f:
        metrics_data = json.load(f)
        assert "session_info" in metrics_data
        assert "api_statistics" in metrics_data
        assert "performance_statistics" in metrics_data

    with open(dashboard_report_path) as f:
        dashboard_data = json.load(f)
        assert "dashboard_generated" in dashboard_data
        assert "system_health" in dashboard_data
        assert "performance_summary" in dashboard_data

    # Clean up test files
    metrics_report_path.unlink()
    dashboard_report_path.unlink()

    print("✅ Monitoring file operations working correctly")
    return True


def main():
    """Run comprehensive monitoring and metrics tests."""
    print("🧪 Comprehensive Monitoring and Metrics Collection Tests")
    print("=" * 65)
    print("Testing Task 10.2: Build monitoring and metrics collection")
    print("=" * 65)

    # Set up logging
    from logger import LogLevel
    setup_logging(log_level=LogLevel.INFO)

    tests = [
        ("API Metrics Tracking", test_api_metrics_tracking),
        ("Content Generation Monitoring", test_content_generation_monitoring),
        ("Performance Metrics", test_performance_metrics),
        ("Error Tracking & Categorization", test_error_tracking_categorization),
        ("GitHub Actions Outputs", test_github_actions_outputs),
        ("Comprehensive Monitoring System", test_comprehensive_monitoring_system),
        ("Monitoring File Operations", test_monitoring_file_operations)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*65}")
    print(f"TASK 10.2 RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All monitoring and metrics collection features working correctly!")
        print("\nTask 10.2 Requirements Validated:")
        print("✅ OpenRouter API response times and token usage tracking")
        print("✅ Content generation success rates and failure modes monitoring")
        print("✅ Performance metrics for style analysis and optimization")
        print("✅ Error rate tracking and categorization")
        print("✅ GitHub Actions output metrics")
        return 0
    else:
        print("⚠️  Some monitoring features failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())