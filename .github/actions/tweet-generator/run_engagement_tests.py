#!/usr/bin/env python3
"""
Test runner for engagement optimization functionality.

This script runs comprehensive tests for hook generation, thread structure optimization,
engagement element integration, and psychological trigger effectiveness.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_engagement_tests():
    """Run engagement optimization tests with detailed output."""

    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("🚀 Running Engagement Optimization Tests")
    print("=" * 50)

    # Run the tests with verbose output
    cmd = [
        sys.executable, "-m", "pytest",
        "test_engagement_optimization.py",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure for debugging
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(f"\nTest execution completed with return code: {result.returncode}")

        if result.returncode == 0:
            print("✅ All engagement optimization tests passed!")
        else:
            print("❌ Some tests failed. Check output above for details.")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_test_categories():
    """Run specific categories of engagement tests."""

    test_categories = [
        ("Hook Generation", "test_optimize_hooks"),
        ("Thread Structure", "test_apply_thread_structure"),
        ("Engagement Elements", "test_add_engagement_elements"),
        ("Hashtag Optimization", "test_optimize_hashtags"),
        ("Visual Formatting", "test_apply_visual_formatting"),
        ("Social Proof", "test_add_social_proof"),
        ("Psychological Triggers", "test_psychological_triggers"),
        ("Engagement Scoring", "test_calculate_engagement_score")
    ]

    print("\n🎯 Running Specific Test Categories")
    print("=" * 50)

    results = {}

    for category_name, test_pattern in test_categories:
        print(f"\n📊 Testing {category_name}...")

        cmd = [
            sys.executable, "-m", "pytest",
            "test_engagement_optimization.py",
            "-k", test_pattern,
            "-v",
            "--tb=line"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print(f"✅ {category_name}: PASSED")
                results[category_name] = "PASSED"
            else:
                print(f"❌ {category_name}: FAILED")
                results[category_name] = "FAILED"
                print(f"   Error: {result.stdout.split('FAILED')[0] if 'FAILED' in result.stdout else 'Unknown error'}")

        except subprocess.TimeoutExpired:
            print(f"⏰ {category_name}: TIMEOUT")
            results[category_name] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {category_name}: ERROR - {e}")
            results[category_name] = "ERROR"

    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 30)

    passed = sum(1 for status in results.values() if status == "PASSED")
    total = len(results)

    for category, status in results.items():
        status_emoji = {"PASSED": "✅", "FAILED": "❌", "TIMEOUT": "⏰", "ERROR": "💥"}
        print(f"{status_emoji.get(status, '❓')} {category}: {status}")

    print(f"\nOverall: {passed}/{total} categories passed")

    return passed == total

if __name__ == "__main__":
    print("Engagement Optimization Test Suite")
    print("==================================")

    # Check if pytest is available
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])

    # Run all tests first
    all_passed = run_engagement_tests()

    # If there are failures, run category-specific tests for better debugging
    if not all_passed:
        print("\n" + "="*50)
        print("Running category-specific tests for debugging...")
        run_specific_test_categories()

    sys.exit(0 if all_passed else 1)