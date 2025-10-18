#!/usr/bin/env python3
"""
Proper test for monitoring system using pip install approach.
"""

import sys
import os
from pathlib import Path

# Set up the path properly
action_dir = Path(__file__).parent
src_dir = action_dir / "src"
sys.path.insert(0, str(src_dir))

def test_monitoring_system():
    """Test the monitoring system components."""
    print("🧪 Testing Tweet Thread Generator Monitoring System")
    print("=" * 60)

    try:
        # Test imports
        print("1. Testing imports...")
        from logger import setup_logging, get_logger, OperationType
        from metrics import setup_metrics_collection, get_metrics_collector, ErrorCategory
        from monitoring import (
            setup_monitoring,
            get_health_monitor,
            get_monitoring_dashboard,
            HealthMonitor,
            MonitoringDashboard,
            HealthStatus
        )
        print("   ✅ All imports successful")

        # Test basic setup
        print("2. Setting up monitoring system...")
        metrics, health_monitor, dashboard = setup_monitoring("test-session")
        logger = get_logger()
        print("   ✅ Monitoring system initialized")

        # Test metrics collection
        print("3. Testing metrics collection...")
        metrics.increment_counter("test_api_calls", 5)
        metrics.set_gauge("test_response_time", 150.5)

        # Record a test API call
        metrics.record_api_call(
            endpoint="https://openrouter.ai/api/v1/chat/completions",
            method="POST",
            response_time_ms=150.0,
            status_code=200,
            tokens_used=100,
            success=True
        )

        # Record test content generation
        metrics.record_content_generation(
            operation_type=OperationType.AI_GENERATION,
            post_slug="test-post",
            model_used="google/gemini-2.5-flash-lite",
            input_characters=500,
            output_characters=280,
            processing_time_ms=1000.0,
            tweets_generated=3,
            hooks_generated=2,
            engagement_score=0.85,
            success=True
        )
        print("   ✅ Metrics collection working")

        # Test health monitoring
        print("4. Testing health monitoring...")
        system_health = health_monitor.perform_health_checks()
        print(f"   📊 Overall health: {system_health.overall_status.value}")
        print(f"   📋 Health checks: {len(system_health.checks)}")
        print(f"   🚨 Active alerts: {len(health_monitor.get_active_alerts())}")

        for check in system_health.checks:
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌",
                "unknown": "❓"
            }.get(check.status.value, "❓")
            print(f"      {status_icon} {check.name}: {check.status.value}")

        print("   ✅ Health monitoring working")

        # Test dashboard
        print("5. Testing monitoring dashboard...")
        dashboard_data = dashboard.generate_dashboard_data()

        key_metrics = dashboard_data["key_metrics"]
        print(f"   📊 API Calls: {key_metrics['total_api_calls']}")
        print(f"   📝 Content Generated: {key_metrics['content_generations']}")
        print(f"   🐦 Tweets Generated: {key_metrics['tweets_generated']}")
        print(f"   🪙 Tokens Used: {key_metrics['tokens_used']}")
        print("   ✅ Dashboard generation working")

        # Test statistics
        print("6. Testing statistics...")
        api_stats = metrics.get_api_statistics()
        content_stats = metrics.get_content_statistics()
        error_stats = metrics.get_error_statistics()

        print(f"   📈 API Success Rate: {api_stats.get('success_rate', 0):.1f}%")
        print(f"   📈 Content Success Rate: {content_stats.get('success_rate', 0):.1f}%")
        print(f"   📈 Total Errors: {error_stats.get('total_errors', 0)}")
        print("   ✅ Statistics working")

        # Test report generation
        print("7. Testing report generation...")

        # Generate comprehensive report
        comprehensive_report = metrics.get_comprehensive_report()
        print(f"   📄 Report sections: {len(comprehensive_report)}")

        # Test summary report
        print("\n" + "=" * 60)
        print("MONITORING SUMMARY REPORT")
        dashboard.print_summary_report()

        print("\n🎉 All monitoring system tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_monitoring_system()
    sys.exit(0 if success else 1)