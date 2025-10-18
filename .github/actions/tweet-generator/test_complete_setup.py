#!/usr/bin/env python3
"""
Complete setup and testing script for GitHub Tweet Thread Generator.

This script performs comprehensive testing including:
- Package management verification
- Dependency installation checks
- Core functionality testing
- Monitoring system validation
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")

    version = sys.version_info
    if version < (3, 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Requires Python 3.8+")
        return False

    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_package_manager():
    """Check if pip is available."""
    print("\n📦 Checking package manager...")

    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True)
        print("✓ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False

def check_required_packages():
    """Check if required packages are installed."""
    print("\n📚 Checking required packages...")

    required_packages = {
        'httpx': 'HTTP client for API calls',
        'pydantic': 'Data validation and settings',
        'github': 'GitHub API client (PyGithub)',
        'tweepy': 'Twitter API client',
        'yaml': 'YAML configuration parsing',
        'nltk': 'Natural language processing',
        'textstat': 'Text readability analysis',
        'emoji': 'Emoji processing',
        'frontmatter': 'Frontmatter parsing'
    }

    missing_packages = []

    for package, description in required_packages.items():
        try:
            # Handle package name variations
            import_name = package
            if package == 'github':
                import_name = 'github'
            elif package == 'yaml':
                import_name = 'yaml'
            elif package == 'frontmatter':
                import_name = 'frontmatter'

            importlib.import_module(import_name)
            print(f"✓ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run 'python install_dependencies.py' to install them")
        return False

    print("✓ All required packages are installed")
    return True

def check_optional_packages():
    """Check optional development packages."""
    print("\n🔧 Checking optional development packages...")

    optional_packages = {
        'pytest': 'Testing framework',
        'black': 'Code formatter',
        'flake8': 'Code linter',
        'mypy': 'Type checker'
    }

    for package, description in optional_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {package} - {description}")
        except ImportError:
            print(f"ℹ️  {package} - {description} (optional)")

def test_core_imports():
    """Test core module imports."""
    print("\n🔍 Testing core imports...")

    try:
        from models import BlogPost, StyleProfile, ThreadData, GeneratorConfig
        from config import ConfigManager
        from logger import setup_logging, get_logger
        from metrics import setup_metrics_collection
        from monitoring import setup_monitoring
        from utils import ensure_directory, safe_filename

        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_models():
    """Test data model functionality."""
    print("\n📊 Testing data models...")

    try:
        from models import BlogPost, GeneratorConfig, StyleProfile

        # Test BlogPost
        post = BlogPost(
            file_path="_posts/test.md",
            title="Test Post",
            content="Test content",
            frontmatter={"title": "Test"},
            canonical_url="https://example.com/test"
        )
        assert post.slug == "test"

        # Test GeneratorConfig
        config = GeneratorConfig()
        assert config.openrouter_model is not None

        # Test StyleProfile
        profile = StyleProfile()
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)

        print("✓ Data models working correctly")
        return True
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False

def test_logging_system():
    """Test logging system."""
    print("\n📝 Testing logging system...")

    try:
        from logger import setup_logging, get_logger, OperationType

        setup_logging()
        logger = get_logger()

        logger.info("Test log message")
        logger.log_operation(OperationType.CONTENT_DETECTION, "test", {})

        print("✓ Logging system working")
        return True
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def test_metrics_system():
    """Test metrics collection system."""
    print("\n📈 Testing metrics system...")

    try:
        from metrics import setup_metrics_collection, ErrorCategory

        metrics = setup_metrics_collection("test-session")

        # Test basic operations
        metrics.increment_counter("test_counter", 1)

        with metrics.time_operation("test_operation"):
            import time
            time.sleep(0.01)

        metrics.record_error(ErrorCategory.VALIDATION_ERROR, "Test error", {})

        # Test statistics
        stats = metrics.get_api_statistics()
        assert isinstance(stats, dict)

        print("✓ Metrics system working")
        return True
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

def test_monitoring_system():
    """Test monitoring system."""
    print("\n🔍 Testing monitoring system...")

    try:
        from monitoring import setup_monitoring, get_health_monitor

        metrics, health_monitor, dashboard = setup_monitoring("test-session")

        # Test health checks
        health_status = health_monitor.perform_health_checks()
        assert hasattr(health_status, 'overall_status')

        # Test dashboard
        dashboard_data = dashboard.generate_dashboard_data()
        assert isinstance(dashboard_data, dict)

        print("✓ Monitoring system working")
        return True
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

def test_file_operations():
    """Test file operations."""
    print("\n💾 Testing file operations...")

    try:
        from utils import ensure_directory, safe_filename
        from metrics import setup_metrics_collection

        # Test directory creation
        test_dir = project_root / "test_output"
        ensure_directory(test_dir)
        assert test_dir.exists()

        # Test safe filename
        safe_name = safe_filename("test/file:name.json")
        assert "/" not in safe_name and ":" not in safe_name

        # Test metrics file operations
        metrics = setup_metrics_collection("test-session")
        report_path = test_dir / "test-report.json"
        metrics.save_metrics_report(str(report_path))

        if report_path.exists():
            report_path.unlink()  # Clean up

        print("✓ File operations working")
        return True
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n⚙️  Testing configuration...")

    try:
        from config import ConfigManager
        from models import ValidationStatus

        # Test environment validation
        env_result = ConfigManager.validate_environment()
        assert hasattr(env_result, 'status')

        # Test config loading
        config = ConfigManager.load_config()
        assert config.openrouter_model is not None

        print("✓ Configuration system working")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_installation_check():
    """Check if installation is needed and offer to install."""
    print("\n🔧 Installation Check")
    print("=" * 40)

    if not check_required_packages():
        install = input("\nWould you like to install missing dependencies? (Y/n): ").strip().lower()
        if install not in ['n', 'no']:
            print("\nRunning dependency installer...")
            try:
                subprocess.run([sys.executable, "install_dependencies.py"], check=True)
                print("✓ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Installation failed: {e}")
                return False

    return True

def main():
    """Run complete setup and testing."""
    print("🚀 GitHub Tweet Thread Generator - Complete Setup Test")
    print("=" * 60)

    # Basic system checks
    system_checks = [
        ("Python Version", check_python_version),
        ("Package Manager", check_package_manager),
    ]

    for check_name, check_func in system_checks:
        if not check_func():
            print(f"\n❌ {check_name} check failed. Please fix this before continuing.")
            return 1

    # Package installation check
    if not run_installation_check():
        return 1

    # Optional packages check
    check_optional_packages()

    # Functionality tests
    functionality_tests = [
        ("Core Imports", test_core_imports),
        ("Data Models", test_data_models),
        ("Logging System", test_logging_system),
        ("Metrics System", test_metrics_system),
        ("Monitoring System", test_monitoring_system),
        ("File Operations", test_file_operations),
        ("Configuration", test_configuration),
    ]

    print(f"\n🧪 Running Functionality Tests")
    print("=" * 40)

    passed = 0
    total = len(functionality_tests)

    for test_name, test_func in functionality_tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")

    # Results
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your setup is ready for development.")
        print("\nNext steps:")
        print("1. Run 'python run_tests.py monitoring' for detailed monitoring tests")
        print("2. Check TESTING_SETUP.md for advanced testing options")
        print("3. Review README.md for usage instructions")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        print("\nTroubleshooting:")
        print("1. Run 'python install_dependencies.py' to install missing packages")
        print("2. Check TESTING_SETUP.md for detailed setup instructions")
        print("3. Ensure you're in the correct directory (.github/actions/tweet-generator)")
        return 1

if __name__ == "__main__":
    sys.exit(main())