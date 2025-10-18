#!/usr/bin/env python3
"""
Simple test for monitoring system components.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Test individual imports
    print("Testing individual imports...")

    from logger import setup_logging, get_logger, OperationType
    print("✅ Logger import successful")

    from metrics import setup_metrics_collection, get_metrics_collector, ErrorCategory
    print("✅ Metrics import successful")

    # Test monitoring import
    import monitoring
    print("✅ Monitoring module import successful")

    # Check if functions exist
    if hasattr(monitoring, 'setup_monitoring'):
        print("✅ setup_monitoring function found")
    else:
        print("❌ setup_monitoring function NOT found")
        print("Available functions:", [name for name in dir(monitoring) if not name.startswith('_')])

    if hasattr(monitoring, 'get_health_monitor'):
        print("✅ get_health_monitor function found")
    else:
        print("❌ get_health_monitor function NOT found")

    if hasattr(monitoring, 'get_monitoring_dashboard'):
        print("✅ get_monitoring_dashboard function found")
    else:
        print("❌ get_monitoring_dashboard function NOT found")

    # Test basic functionality
    print("\nTesting basic functionality...")

    # Set up logging and metrics
    logger = setup_logging()
    metrics = setup_metrics_collection("test-session")

    print("✅ Basic setup successful")

    # Test metrics collection
    metrics.increment_counter("test_counter", 1)
    metrics.set_gauge("test_gauge", 42.0)

    print("✅ Metrics collection successful")

    # Test health monitor
    health_monitor = monitoring.HealthMonitor(metrics)
    api_health = health_monitor.check_api_health()
    print(f"✅ Health check successful: {api_health.status.value}")

    # Test dashboard
    dashboard = monitoring.MonitoringDashboard(metrics)
    dashboard_data = dashboard.generate_dashboard_data()
    print(f"✅ Dashboard generation successful")

    print("\n🎉 All basic monitoring tests passed!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)