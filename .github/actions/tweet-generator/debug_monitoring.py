#!/usr/bin/env python3
"""
Debug monitoring import issues.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    print("Testing imports step by step...")

    # Test basic imports
    import json
    import time
    from datetime import datetime, timezone, timedelta
    from typing import Dict, Any, List, Optional, Tuple
    from pathlib import Path
    from dataclasses import dataclass, field
    from enum import Enum
    print("✅ Basic imports OK")

    # Test logger import
    try:
        from logger import get_logger, OperationType
        print("✅ Logger import OK")
    except Exception as e:
        print(f"❌ Logger import failed: {e}")
        raise

    # Test metrics import
    try:
        from metrics import get_metrics_collector, MetricsCollector, ErrorCategory, setup_metrics_collection
        print("✅ Metrics import OK")
    except Exception as e:
        print(f"❌ Metrics import failed: {e}")
        raise

    # Now try to read and execute the monitoring file line by line
    print("Reading monitoring.py file...")

    with open('.github/actions/tweet-generator/src/monitoring.py', 'r') as f:
        content = f.read()

    print(f"File size: {len(content)} characters")

    # Try to execute it
    print("Executing monitoring.py content...")
    exec(content)

    print("✅ Monitoring file executed successfully")
    print(f"HealthMonitor class: {HealthMonitor}")
    print(f"setup_monitoring function: {setup_monitoring}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()