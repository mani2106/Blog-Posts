#!/usr/bin/env python3
"""
Simple monitoring system test that works with current setup.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_basic_imports():
    """Test basic imports work."""
    print("Testing basic imports...")

    try:
        # Test logger import
        from logger import setup_logging, get_logger
        print("✓ Logger import successful")

        # Test metrics import
        from metrics import setup_metrics_collection
        print("✓ Metrics import successful")

        # Test monitoring import
        from monitoring import setup_monitoring
        print("✓ Monitoring import successful")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_logger_setup():
    """Test logger setup and basic functionality."""
    print("\nTesting logger setup...")

    try:
        from logger import setup_logging, get_logger, OperationType

        # Setup logging
        setup_logging()
        logger = get_logger()

        # Test basic logging
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # Test operation logging
        logger.log_operation(OperationType.CONTENT_DETECTION, "test-post", {"test": "data"})

        print("✓ Logger functionality working")
        return True
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

def test_metrics_basic():
    """Test basic metrics functionality."""
    print("\nTesting metrics collection...")

    try:
        from metrics import setup_metrics_collection, ErrorCategory

        # Setup metrics
        metrics = setup_metrics_collection("test-session")

        # Test counter operations
        metrics.increment_counter("test_counter", 5)
        metrics.increment_counter("test_counter", 3)

        # Test timing operations
        with metrics.time_operation("test_operation"):
            import time
            time.sleep(0.1)  # Simulate work

        # Test error tracking
        metrics.record_error(ErrorCategory.API_ERROR, "Test error", {"context": "test"})

        # Get basic stats
        stats = metrics.get_api_statistics()
        print(f"✓ Metrics working - API stats: {stats}")

        return True
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

def test_monitoring_setup():
    """Test monitoring system setup."""
    print("\nTesting monitoring setup...")

    try:
        from monitoring import setup_monitoring, get_health_monitor, get_monitoring_dashboard

        # Setup monitoring
        metrics, health_monitor, dashboard = setup_monitoring("test-session")

        # Test health monitor
        health_status = health_monitor.perform_health_checks()
        print(f"✓ Health check status: {health_status.overall_status.value}")

        # Test dashboard
        dashboard_data = dashboard.generate_dashboard_data()
        print(f"✓ Dashboard generated at: {dashboard_data.get('dashboard_generated', 'unknown')}")

        return True
    except Exception as e:
        print(f"❌ Monitoring setup test failed: {e}")
        return False

def test_file_operations():
    """Test file operations for monitoring."""
    print("\nTesting file operations...")

    try:
        from metrics import setup_metrics_collection

        # Setup metrics
        metrics = setup_metrics_collection("test-session")

        # Test saving metrics report
        test_output_dir = project_root / "test_output"
        test_output_dir.mkdir(exist_ok=True)

        report_path = test_output_dir / "test-metrics-report.json"
        metrics.save_metrics_report(str(report_path))

        if report_path.exists():
            print(f"✓ Metrics report saved to: {report_path}")
            # Clean up
            report_path.unlink()
            return True
        else:
            print("❌ Metrics report not created")
            return False

    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def main():
    """Run all simple monitoring tests."""
    print("🧪 Simple Monitoring System Tests")
    print("=" * 40)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Logger Setup", test_logger_setup),
        ("Metrics Basic", test_metrics_basic),
        ("Monitoring Setup", test_monitoring_setup),
        ("File Operations", test_file_operations)
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

    print(f"\n{'='*40}")
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All monitoring tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())