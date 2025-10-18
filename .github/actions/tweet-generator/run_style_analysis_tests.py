#!/usr/bin/env python3
"""
Test runner for style analysis functionality.

This script runs the comprehensive style analysis tests and provides
a summary of the test results.
"""

import subprocess
import sys
from pathlib import Path


def run_style_analysis_tests():
    """Run the style analysis tests and return results."""
    print("🧪 Running Style Analysis Tests")
    print("=" * 50)

    # Change to the correct directory
    test_dir = Path(__file__).parent
    test_file = test_dir / "test_style_analysis.py"

    if not test_file.exists():
        print("❌ Test file not found: test_style_analysis.py")
        return False

    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v",
            "--tb=short"
        ],
        cwd=test_dir,
        capture_output=True,
        text=True
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print("\n✅ All style analysis tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main entry point."""
    success = run_style_analysis_tests()

    if success:
        print("\n🎉 Style analysis testing complete - all tests passed!")
        print("\nTest Coverage Summary:")
        print("✓ Vocabulary pattern analysis")
        print("✓ Tone indicator extraction")
        print("✓ Content structure identification")
        print("✓ Emoji usage analysis")
        print("✓ Style profile persistence")
        print("✓ Error handling scenarios")
        print("✓ Integration with mixed content types")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()