#!/usr/bin/env python3
"""
Minimal monitoring test to isolate the issue.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test the imports step by step
try:
    print("Step 1: Testing basic imports...")
    import json
    import time
    from datetime import datetime, timezone, timedelta
    from typing import Dict, Any, List, Optional, Tuple
    from pathlib import Path
    from dataclasses import dataclass, field
    from enum import Enum
    print("✅ Basic imports successful")

    print("Step 2: Testing logger import...")
    from logger import get_logger, OperationType
    print("✅ Logger import successful")

    print("Step 3: Testing metrics import...")
    from metrics import get_metrics_collector, MetricsCollector, ErrorCategory, setup_metrics_collection
    print("✅ Metrics import successful")

    print("Step 4: Testing monitoring classes...")

    # Define the classes directly here to test
    class HealthStatus(str, Enum):
        """System health status levels."""
        HEALTHY = "healthy"
        WARNING = "warning"
        CRITICAL = "critical"
        UNKNOWN = "unknown"

    print("✅ HealthStatus enum created")

    @dataclass
    class HealthCheck:
        """Individual health check result."""
        name: str
        status: HealthStatus
        message: str
        details: Dict[str, Any] = field(default_factory=dict)
        timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    print("✅ HealthCheck dataclass created")

    class HealthMonitor:
        """System health monitoring and alerting."""

        def __init__(self, metrics_collector: MetricsCollector):
            self.metrics = metrics_collector
            self.logger = get_logger()

        def check_api_health(self) -> HealthCheck:
            """Check API connectivity and performance health."""
            return HealthCheck(
                name="api_connectivity",
                status=HealthStatus.UNKNOWN,
                message="No API calls recorded yet",
                details={}
            )

    print("✅ HealthMonitor class created")

    # Test basic functionality
    print("Step 5: Testing functionality...")
    logger = get_logger()
    metrics = setup_metrics_collection("test-session")

    health_monitor = HealthMonitor(metrics)
    health_check = health_monitor.check_api_health()

    print(f"✅ Health check result: {health_check.status.value}")

    print("\n🎉 Minimal monitoring test successful!")

except Exception as e:
    print(f"❌ Test failed at step: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)