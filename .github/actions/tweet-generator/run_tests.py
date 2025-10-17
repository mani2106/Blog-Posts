#!/usr/bin/env python3
"""
Test runner script for GitHub Tweet Thread Generator.

This script sets up the environment and runs tests with proper package management.
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the Python environment for testing."""
    project_root = Path(__file__).parent
    src_path = project_root / "src"

    # Add src directory to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(src_path) not in current_pythonpath:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{src_path}{os.pathsep}{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = str(src_path)

    print(f"✓ Added {src_path} to Python path")
    return project_root

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pytest
        print("✓ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
        print("✓ pytest installed")

    # Check for other test dependencies
    optional_deps = ['pytest-asyncio', 'black', 'flake8']
    for dep in optional_deps:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✓ {dep} is available")
        except ImportError:
            print(f"ℹ️  {dep} not found (optional)")

def install_package_in_dev_mode():
    """Install the package in development mode."""
    project_root = Path(__file__).parent

    print("Installing package in development mode...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], cwd=project_root, check=True, capture_output=True)
        print("✓ Package installed in development mode")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not install in dev mode: {e}")
        print("Continuing with path-based imports...")
        return False

def run_specific_test(test_name):
    """Run a specific test file."""
    project_root = Path(__file__).parent

    test_files = {
        'setup': 'test_setup.py',
        'complete': 'test_complete_setup.py',
        'monitoring': 'test_monitoring.py',
        'monitoring-comprehensive': 'test_monitoring_comprehensive.py',
        'monitoring-simple': 'test_monitoring_simple.py',
        'monitoring-minimal': 'test_monitoring_minimal.py',
        'monitoring-proper': 'test_monitoring_proper.py',
        'auto-posting': 'test_auto_posting.py',
        'all': None  # Run all tests
    }

    if test_name not in test_files:
        print(f"Available tests: {', '.join(test_files.keys())}")
        return False

    if test_name == 'all':
        # Run all test files
        test_pattern = "test_*.py"
        cmd = [sys.executable, "-m", "pytest", test_pattern, "-v"]
    else:
        test_file = test_files[test_name]
        if not (project_root / test_file).exists():
            print(f"❌ Test file {test_file} not found")
            return False
        cmd = [sys.executable, test_file]

    print(f"Running test: {test_name}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main test runner."""
    print("🧪 GitHub Tweet Thread Generator Test Runner")
    print("=" * 50)

    # Setup environment
    project_root = setup_environment()

    # Check dependencies
    check_dependencies()

    # Try to install in dev mode (optional)
    install_package_in_dev_mode()

    # Determine which test to run
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
    else:
        print("\nAvailable tests:")
        print("  setup          - Basic setup and import tests")
        print("  complete       - Complete setup with package management")
        print("  monitoring     - Full monitoring system tests")
        print("  monitoring-comprehensive - Task 10.2 comprehensive monitoring tests")
        print("  monitoring-simple - Simple monitoring tests")
        print("  monitoring-minimal - Minimal monitoring tests")
        print("  auto-posting   - Auto-posting functionality tests")
        print("  all            - Run all tests with pytest")
        print()
        test_name = input("Enter test name (or 'complete' for comprehensive tests): ").strip() or 'complete'

    # Run the test
    success = run_specific_test(test_name)

    if success:
        print("\n🎉 Tests completed successfully!")
        return 0
    else:
        print("\n❌ Tests failed or encountered errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())