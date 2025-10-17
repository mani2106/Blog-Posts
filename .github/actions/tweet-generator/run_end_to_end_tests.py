#!/usr/bin/env python3
"""
End-to-end integration test runner for the GitHub Tweet Thread Generator.

This script runs comprehensive integration tests that validate:
- Complete workflow with sample repositories
- GitHub Actions execution environment
- Configuration loading and validation
- Performance and resource usage

Requirements tested: 1.4, 10.1, 10.6
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="Run end-to-end integration tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", "-t", help="Run specific test by name")
    parser.add_argument("--output", "-o", help="Output results to JSON file")
    parser.add_argument("--github-actions", action="store_true",
                       help="Format output for GitHub Actions")

    args = parser.parse_args()

    # Set up logging level
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        # Import and run tests
        from test_end_to_end import EndToEndTestSuite

        suite = EndToEndTestSuite()

        if args.test:
            # Run specific test
            test_method = getattr(suite, f"test_{args.test}", None)
            if test_method:
                suite.setup_test_environment()
                try:
                    suite.run_test(args.test, test_method)
                finally:
                    suite.cleanup_test_environment()
            else:
                print(f"Test '{args.test}' not found")
                return 1
        else:
            # Run all tests
            results = suite.run_all_tests()

            # Save results if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Results saved to {args.output}")

            # Format for GitHub Actions
            if args.github_actions:
                print(f"::set-output name=tests_run::{results['tests_run']}")
                print(f"::set-output name=tests_passed::{results['tests_passed']}")
                print(f"::set-output name=tests_failed::{results['tests_failed']}")

                if results['tests_failed'] > 0:
                    print("::error::End-to-end integration tests failed")
                    for failure in results['failures']:
                        print(f"::error::{failure['test']}: {failure['error']}")
                else:
                    print("::notice::All end-to-end integration tests passed")

            # Return appropriate exit code
            return 0 if results['tests_failed'] == 0 else 1

    except ImportError as e:
        print(f"Error importing test suite: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())