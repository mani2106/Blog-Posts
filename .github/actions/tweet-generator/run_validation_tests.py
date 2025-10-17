#!/usr/bin/env python3
"""
Test runner for validation and safety tests.

This script runs the comprehensive validation and safety test suite
for the GitHub Tweet Thread Generator.
"""

import os
import sys
import subprocess

def main():
    """Run validation and safety tests."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, 'test_validation_safety.py')

    print("Running Validation and Safety Tests...")
    print("=" * 50)

    try:
        # Try to run with pytest first
        result = subprocess.run([
            sys.executable, '-m', 'pytest', test_file, '-v'
        ], capture_output=True, text=True, cwd=script_dir)

        if result.returncode == 0:
            print("✓ Tests passed with pytest")
            print(result.stdout)
            return True
        else:
            print("pytest failed, falling back to standalone runner")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("pytest not available, using standalone runner")

    # Fallback to standalone runner
    try:
        result = subprocess.run([
            sys.executable, test_file
        ], cwd=script_dir)

        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)