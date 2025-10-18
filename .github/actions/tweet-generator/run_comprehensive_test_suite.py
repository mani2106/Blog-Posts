#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Master test runner that executes all test categories and generates complete reports.
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from test_comprehensive_suite import ComprehensiveTestSuite
from test_performance_benchmarks import PerformanceBenchmark
from test_data_sets import TestDataSets
from mock_services import MockServiceFactory

class MasterTestRunner:
    """Master test runner that orchestrates all test suites."""

    def __init__(self):
        self.logger = self.setup_logger()
        self.start_time = time.time()
        self.results = {
            'execution_info': {
                'start_time': self.start_time,
                'end_time': None,
                'total_duration': None,
                'python_version': sys.version,
                'platform': sys.platform
            },
            'test_suites': {},
            'overall_summary': {},
            'requirements_coverage': {},
            'performance_analysis': {},
            'recommendations': []
        }

    def setup_logger(self):
        """Set up comprehensive logging for the master test runner."""
        logger = logging.getLogger('master_test_runner')
        logger.setLevel(logging.INFO)

        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler for detailed logs
        log_file = os.path.join(os.path.dirname(__file__), 'master_test_results.log')
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def setup_test_environment(self):
        """Set up the test environment and generate test data."""
        self.logger.info("🔧 Setting up test environment...")

        try:
            # Generate test data
            test_data = TestDataSets()
            test_data.save_all_test_data()
            self.logger.info("✅ Test data generated successfully")

            # Initialize mock services
            mock_factory = MockServiceFactory()
            mock_factory.create_test_scenario('successful_workflow')
            self.logger.info("✅ Mock services initialized")

            # Verify dependencies
            self.verify_dependencies()
            self.logger.info("✅ Dependencies verified")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to set up test environment: {e}")
            return False

    def verify_dependencies(self):
        """Verify that all required dependencies are available."""
        required_packages = [
            'pytest', 'httpx', 'pydantic', 'nltk', 'textstat',
            'emoji', 'psutil', 'frontmatter'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            raise Exception(f"Missing required packages: {', '.join(missing_packages)}")

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run all unit test suites using pytest."""
        self.logger.info("🧪 Running Unit Tests...")

        unit_test_files = [
            'test_content_detection.py',
            'test_style_analysis.py',
            'test_ai_integration.py',
            'test_engagement_optimization.py',
            'test_validation_safety.py'
        ]

        unit_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_files': {},
            'execution_time': 0
        }

        start_time = time.time()

        for test_file in unit_test_files:
            if os.path.exists(test_file):
                self.logger.info(f"  Running {test_file}...")

                try:
                    # Run pytest for this file
                    result = subprocess.run([
                        sys.executable, '-m', 'pytest', test_file,
                        '-v', '--tb=short', '--json-report',
                        f'--json-report-file={test_file}.json'
                    ], capture_output=True, text=True, timeout=300)

                    # Parse results if JSON report exists
                    json_report_file = f'{test_file}.json'
                    if os.path.exists(json_report_file):
                        with open(json_report_file, 'r') as f:
                            test_report = json.load(f)

                        file_results = {
                            'tests_collected': test_report.get('summary', {}).get('collected', 0),
                            'tests_passed': test_report.get('summary', {}).get('passed', 0),
                            'tests_failed': test_report.get('summary', {}).get('failed', 0),
                            'duration': test_report.get('duration', 0),
                            'exit_code': result.returncode
                        }
                    else:
                        # Fallback parsing
                        file_results = {
                            'tests_collected': 0,
                            'tests_passed': 1 if result.returncode == 0 else 0,
                            'tests_failed': 0 if result.returncode == 0 else 1,
                            'duration': 0,
                            'exit_code': result.returncode
                        }

                    unit_results['test_files'][test_file] = file_results
                    unit_results['total_tests'] += file_results['tests_collected']
                    unit_results['passed_tests'] += file_results['tests_passed']
                    unit_results['failed_tests'] += file_results['tests_failed']

                except subprocess.TimeoutExpired:
                    self.logger.error(f"  ❌ {test_file} timed out")
                    unit_results['test_files'][test_file] = {
                        'error': 'timeout',
                        'tests_collected': 0,
                        'tests_passed': 0,
                        'tests_failed': 1
                    }
                    unit_results['failed_tests'] += 1

                except Exception as e:
                    self.logger.error(f"  ❌ Error running {test_file}: {e}")
                    unit_results['test_files'][test_file] = {
                        'error': str(e),
                        'tests_collected': 0,
                        'tests_passed': 0,
                        'tests_failed': 1
                    }
                    unit_results['failed_tests'] += 1

        unit_results['execution_time'] = time.time() - start_time
        unit_results['success_rate'] = (
            (unit_results['passed_tests'] / unit_results['total_tests']) * 100
            if unit_results['total_tests'] > 0 else 0
        )

        return unit_results

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration test suites."""
        self.logger.info("🔗 Running Integration Tests...")

        integration_test_files = [
            'test_github_integration.py',
            'test_twitter_integration.py',
            'test_end_to_end.py'
        ]

        integration_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_files': {},
            'execution_time': 0
        }

        start_time = time.time()

        for test_file in integration_test_files:
            if os.path.exists(test_file):
                self.logger.info(f"  Running {test_file}...")

                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'pytest', test_file,
                        '-v', '--tb=short'
                    ], capture_output=True, text=True, timeout=600)

                    # Simple result parsing
                    file_results = {
                        'exit_code': result.returncode,
                        'tests_passed': 1 if result.returncode == 0 else 0,
                        'tests_failed': 0 if result.returncode == 0 else 1,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }

                    integration_results['test_files'][test_file] = file_results
                    integration_results['total_tests'] += 1
                    integration_results['passed_tests'] += file_results['tests_passed']
                    integration_results['failed_tests'] += file_results['tests_failed']

                except Exception as e:
                    self.logger.error(f"  ❌ Error running {test_file}: {e}")
                    integration_results['test_files'][test_file] = {
                        'error': str(e),
                        'tests_passed': 0,
                        'tests_failed': 1
                    }
                    integration_results['failed_tests'] += 1
                    integration_results['total_tests'] += 1

        integration_results['execution_time'] = time.time() - start_time
        integration_results['success_rate'] = (
            (integration_results['passed_tests'] / integration_results['total_tests']) * 100
            if integration_results['total_tests'] > 0 else 0
        )

        return integration_results

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run the comprehensive test suite."""
        self.logger.info("📋 Running Comprehensive Test Suite...")

        try:
            comprehensive_suite = ComprehensiveTestSuite()
            results = comprehensive_suite.run_all_tests()

            return {
                'success': True,
                'results': results,
                'execution_time': results['overall']['total_duration'],
                'success_rate': results['overall']['success_rate'],
                'requirements_coverage': results['overall']['requirements_coverage']
            }

        except Exception as e:
            self.logger.error(f"❌ Comprehensive test suite failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0,
                'success_rate': 0,
                'requirements_coverage': 0
            }

    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks."""
        self.logger.info("⚡ Running Performance Benchmarks...")

        try:
            benchmark = PerformanceBenchmark()
            results = benchmark.run_all_benchmarks()

            return {
                'success': True,
                'results': results,
                'execution_time': results['overall']['total_benchmark_time'],
                'regressions_detected': results['overall']['regressions_detected'],
                'critical_regressions': results['overall']['critical_regressions']
            }

        except Exception as e:
            self.logger.error(f"❌ Performance benchmarks failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0,
                'regressions_detected': 0,
                'critical_regressions': 0
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report."""
        self.logger.info("🚀 Starting Master Test Suite Execution")
        self.logger.info("=" * 80)

        # Set up test environment
        if not self.setup_test_environment():
            return {'success': False, 'error': 'Failed to set up test environment'}

        try:
            # Run all test categories
            self.results['test_suites']['unit_tests'] = self.run_unit_tests()
            self.results['test_suites']['integration_tests'] = self.run_integration_tests()
            self.results['test_suites']['comprehensive_tests'] = self.run_comprehensive_tests()
            self.results['test_suites']['performance_benchmarks'] = self.run_performance_benchmarks()

            # Calculate overall summary
            self.calculate_overall_summary()

            # Generate analysis and recommendations
            self.generate_analysis()

            # Generate reports
            self.generate_master_report()
            self.save_results()

            return self.results

        except Exception as e:
            self.logger.error(f"❌ Master test execution failed: {e}")
            return {'success': False, 'error': str(e)}

        finally:
            self.results['execution_info']['end_time'] = time.time()
            self.results['execution_info']['total_duration'] = (
                self.results['execution_info']['end_time'] - self.results['execution_info']['start_time']
            )

    def calculate_overall_summary(self):
        """Calculate overall test summary across all suites."""
        summary = {
            'total_test_suites': len(self.results['test_suites']),
            'successful_suites': 0,
            'failed_suites': 0,
            'total_tests_run': 0,
            'total_tests_passed': 0,
            'total_tests_failed': 0,
            'overall_success_rate': 0,
            'critical_issues': 0,
            'performance_regressions': 0
        }

        for suite_name, suite_results in self.results['test_suites'].items():
            if suite_results.get('success', True):
                summary['successful_suites'] += 1
            else:
                summary['failed_suites'] += 1

            # Aggregate test counts
            if 'total_tests' in suite_results:
                summary['total_tests_run'] += suite_results['total_tests']
                summary['total_tests_passed'] += suite_results.get('passed_tests', 0)
                summary['total_tests_failed'] += suite_results.get('failed_tests', 0)

            # Check for critical issues
            if suite_name == 'comprehensive_tests' and suite_results.get('success'):
                results = suite_results.get('results', {})
                if 'suites' in results:
                    for sub_suite, sub_results in results['suites'].items():
                        if sub_suite in ['security_safety', 'validation_safety']:
                            if sub_results.get('tests_failed', 0) > 0:
                                summary['critical_issues'] += sub_results['tests_failed']

            # Check performance regressions
            if suite_name == 'performance_benchmarks' and suite_results.get('success'):
                summary['performance_regressions'] += suite_results.get('critical_regressions', 0)

        # Calculate overall success rate
        if summary['total_tests_run'] > 0:
            summary['overall_success_rate'] = (
                (summary['total_tests_passed'] / summary['total_tests_run']) * 100
            )

        self.results['overall_summary'] = summary

    def generate_analysis(self):
        """Generate analysis and recommendations based on test results."""
        summary = self.results['overall_summary']
        recommendations = []

        # Performance analysis
        performance_results = self.results['test_suites'].get('performance_benchmarks', {})
        if performance_results.get('success'):
            perf_data = performance_results.get('results', {})
            if perf_data.get('overall', {}).get('critical_regressions', 0) > 0:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'issue': 'Critical performance regressions detected',
                    'recommendation': 'Review and optimize performance-critical components immediately'
                })
            elif perf_data.get('overall', {}).get('regressions_detected', 0) > 3:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'medium',
                    'issue': 'Multiple performance regressions detected',
                    'recommendation': 'Schedule performance optimization review'
                })

        # Security analysis
        comprehensive_results = self.results['test_suites'].get('comprehensive_tests', {})
        if comprehensive_results.get('success'):
            comp_data = comprehensive_results.get('results', {})
            if 'suites' in comp_data:
                security_results = comp_data['suites'].get('security_safety', {})
                if security_results.get('tests_failed', 0) > 0:
                    recommendations.append({
                        'category': 'security',
                        'priority': 'critical',
                        'issue': 'Security test failures detected',
                        'recommendation': 'Address all security issues before deployment'
                    })

        # Coverage analysis
        if comprehensive_results.get('success'):
            coverage = comprehensive_results.get('requirements_coverage', 0)
            if coverage < 80:
                recommendations.append({
                    'category': 'coverage',
                    'priority': 'medium',
                    'issue': f'Requirements coverage is {coverage:.1f}%',
                    'recommendation': 'Add tests to improve requirements coverage'
                })

        # Overall quality assessment
        if summary['overall_success_rate'] < 85:
            recommendations.append({
                'category': 'quality',
                'priority': 'high',
                'issue': f'Overall test success rate is {summary["overall_success_rate"]:.1f}%',
                'recommendation': 'Fix failing tests to improve system reliability'
            })

        self.results['recommendations'] = recommendations

    def generate_master_report(self):
        """Generate comprehensive master test report."""
        print("\n" + "=" * 100)
        print("MASTER TEST SUITE EXECUTION REPORT")
        print("=" * 100)

        # Execution info
        exec_info = self.results['execution_info']
        print(f"📊 EXECUTION SUMMARY:")
        print(f"   Start Time: {datetime.fromtimestamp(exec_info['start_time']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Duration: {exec_info['total_duration']:.2f} seconds")
        print(f"   Python Version: {exec_info['python_version'].split()[0]}")
        print(f"   Platform: {exec_info['platform']}")

        # Overall summary
        summary = self.results['overall_summary']
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Test Suites: {summary['successful_suites']}/{summary['total_test_suites']} successful")
        print(f"   Total Tests: {summary['total_tests_passed']}/{summary['total_tests_run']} passed")
        print(f"   Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"   Critical Issues: {summary['critical_issues']}")
        print(f"   Performance Regressions: {summary['performance_regressions']}")

        # Suite breakdown
        print(f"\n📋 TEST SUITE BREAKDOWN:")
        for suite_name, suite_results in self.results['test_suites'].items():
            status = "✅ PASS" if suite_results.get('success', True) else "❌ FAIL"
            success_rate = suite_results.get('success_rate', 0)
            duration = suite_results.get('execution_time', 0)

            print(f"   {suite_name.replace('_', ' ').title()}: {status}")
            print(f"      Success Rate: {success_rate:.1f}%")
            print(f"      Duration: {duration:.2f}s")

            if not suite_results.get('success', True) and 'error' in suite_results:
                print(f"      Error: {suite_results['error']}")

        # Requirements coverage
        comprehensive_results = self.results['test_suites'].get('comprehensive_tests', {})
        if comprehensive_results.get('success'):
            coverage = comprehensive_results.get('requirements_coverage', 0)
            print(f"\n📋 REQUIREMENTS COVERAGE: {coverage:.1f}%")

        # Performance highlights
        performance_results = self.results['test_suites'].get('performance_benchmarks', {})
        if performance_results.get('success'):
            perf_data = performance_results.get('results', {})
            if 'overall' in perf_data:
                print(f"\n⚡ PERFORMANCE HIGHLIGHTS:")
                print(f"   Benchmark Time: {perf_data['overall']['total_benchmark_time']:.2f}s")
                print(f"   Regressions: {perf_data['overall']['regressions_detected']}")
                print(f"   Critical Regressions: {perf_data['overall']['critical_regressions']}")

        # Recommendations
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in self.results['recommendations']:
                priority_icon = {"critical": "🚨", "high": "⚠️", "medium": "📝"}.get(rec['priority'], "ℹ️")
                print(f"   {priority_icon} {rec['category'].upper()}: {rec['issue']}")
                print(f"      → {rec['recommendation']}")

        # Final verdict
        print(f"\n🏆 FINAL VERDICT:")
        if summary['critical_issues'] > 0:
            print("   🚨 CRITICAL ISSUES DETECTED - Do not deploy to production")
        elif summary['performance_regressions'] > 0:
            print("   ⚠️  PERFORMANCE CONCERNS - Review before deployment")
        elif summary['overall_success_rate'] >= 95:
            print("   🎉 EXCELLENT - System is production-ready!")
        elif summary['overall_success_rate'] >= 85:
            print("   ✅ GOOD - System is functional with minor issues")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Address failing tests before deployment")

        print("=" * 100)

    def save_results(self):
        """Save all test results to files."""
        # Save master results
        master_results_file = os.path.join(os.path.dirname(__file__), 'master_test_results.json')
        with open(master_results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Generate markdown report
        self.generate_markdown_report()

        # Generate JUnit XML for CI/CD
        self.generate_junit_xml()

        self.logger.info(f"📊 Master test results saved to: {master_results_file}")

    def generate_markdown_report(self):
        """Generate markdown report for documentation."""
        report_file = os.path.join(os.path.dirname(__file__), 'MASTER_TEST_REPORT.md')

        with open(report_file, 'w') as f:
            f.write("# Master Test Suite Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration:** {self.results['execution_info']['total_duration']:.2f} seconds\n\n")

            # Executive Summary
            summary = self.results['overall_summary']
            f.write("## Executive Summary\n\n")
            f.write(f"- **Overall Success Rate:** {summary['overall_success_rate']:.1f}%\n")
            f.write(f"- **Test Suites:** {summary['successful_suites']}/{summary['total_test_suites']} successful\n")
            f.write(f"- **Total Tests:** {summary['total_tests_passed']}/{summary['total_tests_run']} passed\n")
            f.write(f"- **Critical Issues:** {summary['critical_issues']}\n")
            f.write(f"- **Performance Regressions:** {summary['performance_regressions']}\n\n")

            # Test Suite Details
            f.write("## Test Suite Results\n\n")
            for suite_name, suite_results in self.results['test_suites'].items():
                status = "✅ PASS" if suite_results.get('success', True) else "❌ FAIL"
                f.write(f"### {suite_name.replace('_', ' ').title()} {status}\n\n")
                f.write(f"- **Success Rate:** {suite_results.get('success_rate', 0):.1f}%\n")
                f.write(f"- **Duration:** {suite_results.get('execution_time', 0):.2f}s\n")

                if not suite_results.get('success', True) and 'error' in suite_results:
                    f.write(f"- **Error:** {suite_results['error']}\n")
                f.write("\n")

            # Recommendations
            if self.results['recommendations']:
                f.write("## Recommendations\n\n")
                for rec in self.results['recommendations']:
                    f.write(f"### {rec['category'].title()} ({rec['priority'].upper()})\n")
                    f.write(f"**Issue:** {rec['issue']}\n\n")
                    f.write(f"**Recommendation:** {rec['recommendation']}\n\n")

    def generate_junit_xml(self):
        """Generate JUnit XML for CI/CD integration."""
        try:
            import xml.etree.ElementTree as ET

            # Create root element
            testsuites = ET.Element('testsuites')
            testsuites.set('name', 'GitHub Tweet Thread Generator Master Suite')
            testsuites.set('tests', str(self.results['overall_summary']['total_tests_run']))
            testsuites.set('failures', str(self.results['overall_summary']['total_tests_failed']))
            testsuites.set('time', str(self.results['execution_info']['total_duration']))

            # Add each test suite
            for suite_name, suite_results in self.results['test_suites'].items():
                testsuite = ET.SubElement(testsuites, 'testsuite')
                testsuite.set('name', suite_name)
                testsuite.set('tests', str(suite_results.get('total_tests', 1)))
                testsuite.set('failures', str(suite_results.get('failed_tests', 0)))
                testsuite.set('time', str(suite_results.get('execution_time', 0)))

                # Add test case
                testcase = ET.SubElement(testsuite, 'testcase')
                testcase.set('name', f'{suite_name}_execution')
                testcase.set('classname', 'MasterTestSuite')

                if not suite_results.get('success', True):
                    failure = ET.SubElement(testcase, 'failure')
                    failure.set('message', suite_results.get('error', 'Test suite failed'))

            # Write XML file
            xml_file = os.path.join(os.path.dirname(__file__), 'master_junit_results.xml')
            tree = ET.ElementTree(testsuites)
            tree.write(xml_file, encoding='utf-8', xml_declaration=True)

            self.logger.info(f"📊 JUnit XML report generated: {xml_file}")

        except Exception as e:
            self.logger.warning(f"Failed to generate JUnit XML: {e}")


def main():
    """Main execution function."""
    runner = MasterTestRunner()

    try:
        results = runner.run_all_tests()

        if not results.get('success', True):
            runner.logger.error("❌ Master test suite execution failed!")
            return 2

        # Determine exit code based on results
        summary = results.get('overall_summary', {})

        if summary.get('critical_issues', 0) > 0:
            runner.logger.error("🚨 Critical issues detected!")
            return 1
        elif summary.get('performance_regressions', 0) > 0:
            runner.logger.warning("⚠️  Performance regressions detected!")
            return 1
        elif summary.get('overall_success_rate', 0) < 80:
            runner.logger.warning("⚠️  Low overall success rate!")
            return 1
        else:
            runner.logger.info("🎉 All tests completed successfully!")
            return 0

    except Exception as e:
        runner.logger.error(f"💥 Master test execution crashed: {e}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)