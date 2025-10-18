#!/usr/bin/env python3
"""
Performance Benchmarks and Regression Tests
Comprehensive performance testing for the GitHub Tweet Thread Generator.
"""

import os
import sys
import time
import json
import psutil
import tracemalloc
from typing import Dict, Any, List, Tuple
from pathlib import Path
import statistics

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from test_data_sets import TestDataSets
from mock_services import MockServiceFactory

# Import components to test
from src.content_detector import ContentDetector
from src.style_analyzer import StyleAnalyzer
from src.ai_orchestrator import AIOrchestrator
from src.engagement_optimizer import EngagementOptimizer
from src.content_validator import ContentValidator
from src.output_manager import OutputManager

class PerformanceBenchmark:
    """Performance benchmarking and regression testing suite."""

    def __init__(self):
        self.test_data = TestDataSets()
        self.mock_factory = MockServiceFactory()
        self.results = {
            'benchmarks': {},
            'regression_tests': {},
            'memory_profiles': {},
            'performance_trends': {}
        }
        self.baseline_metrics = self.load_baseline_metrics()

    def load_baseline_metrics(self) -> Dict[str, Any]:
        """Load baseline performance metrics for regression testing."""
        baseline_file = os.path.join(os.path.dirname(__file__), 'performance_baseline.json')

        if os.path.exists(baseline_file):
            with open(baseline_file, 'r') as f:
                return json.load(f)
        else:
            # Default baseline metrics (these should be updated after initial runs)
            return {
                'content_detection_small': {'max_time': 2.0, 'max_memory': 50},
                'content_detection_large': {'max_time': 10.0, 'max_memory': 200},
                'style_analysis_small': {'max_time': 5.0, 'max_memory': 100},
                'style_analysis_large': {'max_time': 30.0, 'max_memory': 500},
                'thread_generation': {'max_time': 15.0, 'max_memory': 100},
                'engagement_optimization': {'max_time': 3.0, 'max_memory': 50},
                'content_validation': {'max_time': 1.0, 'max_memory': 25},
                'end_to_end_workflow': {'max_time': 60.0, 'max_memory': 300}
            }

    def measure_performance(self, func, *args, **kwargs) -> Tuple[Any, Dict[str, float]]:
        """Measure execution time and memory usage of a function."""
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Measure execution time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Measure memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        metrics = {
            'execution_time': end_time - start_time,
            'memory_used': final_memory - initial_memory,
            'peak_memory': peak / 1024 / 1024,  # MB
            'current_memory': current / 1024 / 1024  # MB
        }

        return result, metrics

    def benchmark_content_detection(self) -> Dict[str, Any]:
        """Benchmark content detection performance."""
        print("🔍 Benchmarking Content Detection...")

        detector = ContentDetector()
        benchmarks = {}

        # Test with different repository sizes
        test_scenarios = [
            ('small_repo', 5),
            ('medium_repo', 25),
            ('large_repo', 100)
        ]

        for scenario_name, post_count in test_scenarios:
            print(f"  Testing {scenario_name} ({post_count} posts)...")

            # Create test repository
            test_repo_dir = self.create_test_repo(post_count)

            # Benchmark detection
            def detect_posts():
                return detector.detect_changed_posts(test_repo_dir)

            result, metrics = self.measure_performance(detect_posts)

            benchmarks[scenario_name] = {
                'posts_detected': len(result) if result else 0,
                'posts_in_repo': post_count,
                **metrics
            }

            # Check against baseline
            baseline_key = f'content_detection_{scenario_name.split("_")[0]}'
            if baseline_key in self.baseline_metrics:
                baseline = self.baseline_metrics[baseline_key]
                benchmarks[scenario_name]['regression_check'] = {
                    'time_regression': metrics['execution_time'] > baseline['max_time'],
                    'memory_regression': metrics['memory_used'] > baseline['max_memory'],
                    'baseline_time': baseline['max_time'],
                    'baseline_memory': baseline['max_memory']
                }

        return benchmarks

    def benchmark_style_analysis(self) -> Dict[str, Any]:
        """Benchmark style analysis performance."""
        print("🎨 Benchmarking Style Analysis...")

        analyzer = StyleAnalyzer()
        benchmarks = {}

        test_scenarios = [
            ('small_blog', 5),
            ('medium_blog', 25),
            ('large_blog', 100)
        ]

        for scenario_name, post_count in test_scenarios:
            print(f"  Testing {scenario_name} ({post_count} posts)...")

            # Create test posts
            test_posts = self.create_test_posts(post_count)

            # Benchmark style analysis
            def analyze_style():
                return analyzer.build_style_profile(test_posts)

            result, metrics = self.measure_performance(analyze_style)

            benchmarks[scenario_name] = {
                'posts_analyzed': post_count,
                'profile_generated': result is not None,
                **metrics
            }

            # Check regression
            baseline_key = f'style_analysis_{scenario_name.split("_")[0]}'
            if baseline_key in self.baseline_metrics:
                baseline = self.baseline_metrics[baseline_key]
                benchmarks[scenario_name]['regression_check'] = {
                    'time_regression': metrics['execution_time'] > baseline['max_time'],
                    'memory_regression': metrics['memory_used'] > baseline['max_memory']
                }

        return benchmarks

    def benchmark_ai_orchestration(self) -> Dict[str, Any]:
        """Benchmark AI orchestration performance."""
        print("🤖 Benchmarking AI Orchestration...")

        # Use mock API for consistent testing
        self.mock_factory.create_test_scenario('successful_workflow')
        orchestrator = AIOrchestrator(api_client=self.mock_factory.openrouter)

        benchmarks = {}
        test_posts = [
            self.test_data.get_technical_tutorial_post(),
            self.test_data.get_personal_experience_post(),
            self.test_data.get_data_science_post()
        ]

        for i, post_data in enumerate(test_posts):
            scenario_name = f'post_type_{i+1}'
            print(f"  Testing {scenario_name}...")

            # Create blog post object
            from src.models import BlogPost
            post = BlogPost(
                file_path=post_data['file_path'],
                title=post_data['frontmatter']['title'],
                content=post_data['content'],
                frontmatter=post_data['frontmatter'],
                canonical_url=post_data['frontmatter']['canonical_url'],
                categories=post_data['frontmatter']['categories']
            )

            # Benchmark thread generation
            def generate_thread():
                return orchestrator.generate_thread(post)

            result, metrics = self.measure_performance(generate_thread)

            benchmarks[scenario_name] = {
                'content_length': len(post.content),
                'thread_generated': result is not None,
                **metrics
            }

        return benchmarks

    def benchmark_engagement_optimization(self) -> Dict[str, Any]:
        """Benchmark engagement optimization performance."""
        print("🚀 Benchmarking Engagement Optimization...")

        optimizer = EngagementOptimizer()
        benchmarks = {}

        test_scenarios = [
            ('short_content', 'Short tip about productivity'),
            ('medium_content', 'A detailed explanation of a technical concept with examples and code snippets that demonstrates the implementation.'),
            ('long_content', self.test_data.get_technical_tutorial_post()['content'][:1000])
        ]

        for scenario_name, content in test_scenarios:
            print(f"  Testing {scenario_name}...")

            def optimize_content():
                hooks = optimizer.generate_hooks(content, count=5)
                optimized = optimizer.optimize_for_engagement(content)
                return hooks, optimized

            result, metrics = self.measure_performance(optimize_content)

            benchmarks[scenario_name] = {
                'content_length': len(content),
                'hooks_generated': len(result[0]) if result[0] else 0,
                'optimization_applied': result[1] is not None,
                **metrics
            }

        return benchmarks

    def benchmark_content_validation(self) -> Dict[str, Any]:
        """Benchmark content validation performance."""
        print("✅ Benchmarking Content Validation...")

        validator = ContentValidator()
        benchmarks = {}

        # Test different validation scenarios
        test_scenarios = [
            ('valid_tweets', ['Short tweet', 'Another valid tweet', 'Third tweet']),
            ('long_tweets', ['This is a very long tweet that exceeds the character limit and should be flagged by the validator'] * 5),
            ('mixed_content', ['Valid tweet', 'This tweet is way too long and contains inappropriate content that should be filtered out by the safety mechanisms', 'Another valid tweet'])
        ]

        for scenario_name, tweets in test_scenarios:
            print(f"  Testing {scenario_name}...")

            def validate_content():
                results = []
                for tweet in tweets:
                    result = validator.validate_tweet(tweet)
                    results.append(result)
                return results

            result, metrics = self.measure_performance(validate_content)

            benchmarks[scenario_name] = {
                'tweets_validated': len(tweets),
                'validation_results': len(result) if result else 0,
                **metrics
            }

        return benchmarks

    def benchmark_end_to_end_workflow(self) -> Dict[str, Any]:
        """Benchmark complete end-to-end workflow."""
        print("🔄 Benchmarking End-to-End Workflow...")

        # Set up mock services
        self.mock_factory.create_test_scenario('successful_workflow')

        # Create test repository
        test_repo_dir = self.create_test_repo(3)

        def run_complete_workflow():
            # Simulate the complete workflow
            detector = ContentDetector()
            analyzer = StyleAnalyzer()
            orchestrator = AIOrchestrator(
                api_key="test_key",
                planning_model="test/planning-model",
                creative_model="test/creative-model",
                verification_model="test/verification-model"
            )
            optimizer = EngagementOptimizer()
            validator = ContentValidator()
            output_manager = OutputManager(
                github_client=self.mock_factory.github,
                twitter_client=self.mock_factory.twitter
            )

            # Step 1: Detect content
            posts = detector.detect_changed_posts(test_repo_dir)

            # Step 2: Analyze style
            style_profile = analyzer.build_style_profile([])

            # Step 3: Generate threads
            threads = []
            for post in posts[:1]:  # Test with one post
                thread = orchestrator.generate_thread(post, style_profile)
                if thread:
                    threads.append(thread)

            # Step 4: Validate content
            for thread in threads:
                validator.validate_thread(thread)

            # Step 5: Create output
            for thread in threads:
                output_manager.save_thread_draft(thread)

            return len(threads)

        result, metrics = self.measure_performance(run_complete_workflow)

        benchmark = {
            'threads_generated': result,
            'workflow_completed': result > 0,
            **metrics
        }

        # Check against baseline
        if 'end_to_end_workflow' in self.baseline_metrics:
            baseline = self.baseline_metrics['end_to_end_workflow']
            benchmark['regression_check'] = {
                'time_regression': metrics['execution_time'] > baseline['max_time'],
                'memory_regression': metrics['memory_used'] > baseline['max_memory']
            }

        return benchmark

    def run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests against baseline performance."""
        print("🔄 Running Regression Tests...")

        regression_results = {}

        # Run all benchmarks
        benchmarks = {
            'content_detection': self.benchmark_content_detection(),
            'style_analysis': self.benchmark_style_analysis(),
            'ai_orchestration': self.benchmark_ai_orchestration(),
            'engagement_optimization': self.benchmark_engagement_optimization(),
            'content_validation': self.benchmark_content_validation(),
            'end_to_end_workflow': self.benchmark_end_to_end_workflow()
        }

        # Analyze regressions
        total_regressions = 0
        critical_regressions = 0

        for category, category_benchmarks in benchmarks.items():
            if isinstance(category_benchmarks, dict) and 'regression_check' in category_benchmarks:
                # Single benchmark
                regression_check = category_benchmarks['regression_check']
                if regression_check.get('time_regression') or regression_check.get('memory_regression'):
                    total_regressions += 1
                    if category in ['end_to_end_workflow', 'ai_orchestration']:
                        critical_regressions += 1
            else:
                # Multiple benchmarks in category
                for scenario, benchmark in category_benchmarks.items():
                    if isinstance(benchmark, dict) and 'regression_check' in benchmark:
                        regression_check = benchmark['regression_check']
                        if regression_check.get('time_regression') or regression_check.get('memory_regression'):
                            total_regressions += 1
                            if category in ['style_analysis', 'content_detection']:
                                critical_regressions += 1

        regression_results = {
            'total_regressions': total_regressions,
            'critical_regressions': critical_regressions,
            'regression_threshold_exceeded': critical_regressions > 0,
            'benchmarks': benchmarks
        }

        return regression_results

    def run_memory_profiling(self) -> Dict[str, Any]:
        """Run detailed memory profiling tests."""
        print("🧠 Running Memory Profiling...")

        memory_profiles = {}

        # Test memory usage patterns
        test_scenarios = [
            ('small_workload', lambda: self.create_test_posts(5)),
            ('medium_workload', lambda: self.create_test_posts(25)),
            ('large_workload', lambda: self.create_test_posts(100))
        ]

        for scenario_name, workload_func in test_scenarios:
            print(f"  Profiling {scenario_name}...")

            # Multiple runs for statistical analysis
            memory_measurements = []
            time_measurements = []

            for run in range(5):
                result, metrics = self.measure_performance(workload_func)
                memory_measurements.append(metrics['memory_used'])
                time_measurements.append(metrics['execution_time'])

            memory_profiles[scenario_name] = {
                'memory_stats': {
                    'mean': statistics.mean(memory_measurements),
                    'median': statistics.median(memory_measurements),
                    'stdev': statistics.stdev(memory_measurements) if len(memory_measurements) > 1 else 0,
                    'max': max(memory_measurements),
                    'min': min(memory_measurements)
                },
                'time_stats': {
                    'mean': statistics.mean(time_measurements),
                    'median': statistics.median(time_measurements),
                    'stdev': statistics.stdev(time_measurements) if len(time_measurements) > 1 else 0,
                    'max': max(time_measurements),
                    'min': min(time_measurements)
                },
                'runs': len(memory_measurements)
            }

        return memory_profiles

    def create_test_repo(self, post_count: int) -> str:
        """Create a test repository with specified number of posts."""
        test_repo_dir = os.path.join(os.path.dirname(__file__), f'test_repo_{post_count}')
        os.makedirs(test_repo_dir, exist_ok=True)

        # Create _posts directory
        posts_dir = os.path.join(test_repo_dir, '_posts')
        os.makedirs(posts_dir, exist_ok=True)

        # Create test posts
        base_posts = [
            self.test_data.get_technical_tutorial_post(),
            self.test_data.get_personal_experience_post(),
            self.test_data.get_data_science_post(),
            self.test_data.get_short_tip_post(),
            self.test_data.get_controversial_opinion_post()
        ]

        for i in range(post_count):
            post_data = base_posts[i % len(base_posts)]
            filename = f'2024-{i+1:02d}-{i+1:02d}-test-post-{i+1}.md'
            filepath = os.path.join(posts_dir, filename)

            # Create frontmatter
            frontmatter_lines = ['---']
            for key, value in post_data['frontmatter'].items():
                if isinstance(value, list):
                    frontmatter_lines.append(f'{key}:')
                    for v in value:
                        frontmatter_lines.append(f'  - {v}')
                else:
                    frontmatter_lines.append(f'{key}: {value}')
            frontmatter_lines.append('---\n')

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(frontmatter_lines))
                f.write(post_data['content'])

        return test_repo_dir

    def create_test_posts(self, count: int) -> List[str]:
        """Create test posts for analysis."""
        base_posts = [
            self.test_data.get_technical_tutorial_post()['content'],
            self.test_data.get_personal_experience_post()['content'],
            self.test_data.get_data_science_post()['content']
        ]

        posts = []
        for i in range(count):
            posts.append(base_posts[i % len(base_posts)])

        return posts

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks and tests."""
        print("🚀 Starting Comprehensive Performance Benchmarks")
        print("=" * 60)

        start_time = time.time()

        # Run all benchmark categories
        self.results['benchmarks']['content_detection'] = self.benchmark_content_detection()
        self.results['benchmarks']['style_analysis'] = self.benchmark_style_analysis()
        self.results['benchmarks']['ai_orchestration'] = self.benchmark_ai_orchestration()
        self.results['benchmarks']['engagement_optimization'] = self.benchmark_engagement_optimization()
        self.results['benchmarks']['content_validation'] = self.benchmark_content_validation()
        self.results['benchmarks']['end_to_end_workflow'] = self.benchmark_end_to_end_workflow()

        # Run regression tests
        self.results['regression_tests'] = self.run_regression_tests()

        # Run memory profiling
        self.results['memory_profiles'] = self.run_memory_profiling()

        # Calculate overall metrics
        total_time = time.time() - start_time
        self.results['overall'] = {
            'total_benchmark_time': total_time,
            'benchmarks_run': len(self.results['benchmarks']),
            'regressions_detected': self.results['regression_tests']['total_regressions'],
            'critical_regressions': self.results['regression_tests']['critical_regressions']
        }

        # Generate reports
        self.generate_performance_report()
        self.save_results()

        return self.results

    def generate_performance_report(self):
        """Generate comprehensive performance report."""
        print("\n" + "=" * 80)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)

        overall = self.results['overall']
        print(f"📊 OVERALL METRICS:")
        print(f"   Total Benchmark Time: {overall['total_benchmark_time']:.2f} seconds")
        print(f"   Benchmarks Run: {overall['benchmarks_run']}")
        print(f"   Regressions Detected: {overall['regressions_detected']}")
        print(f"   Critical Regressions: {overall['critical_regressions']}")

        # Benchmark summary
        print(f"\n🏃 BENCHMARK SUMMARY:")
        for category, benchmarks in self.results['benchmarks'].items():
            print(f"   {category.replace('_', ' ').title()}:")

            if isinstance(benchmarks, dict) and 'execution_time' in benchmarks:
                # Single benchmark
                print(f"      Time: {benchmarks['execution_time']:.2f}s")
                print(f"      Memory: {benchmarks['memory_used']:.1f}MB")
            else:
                # Multiple benchmarks
                for scenario, benchmark in benchmarks.items():
                    if isinstance(benchmark, dict) and 'execution_time' in benchmark:
                        print(f"      {scenario}: {benchmark['execution_time']:.2f}s, {benchmark['memory_used']:.1f}MB")

        # Regression analysis
        regression_tests = self.results['regression_tests']
        print(f"\n🔄 REGRESSION ANALYSIS:")
        if regression_tests['critical_regressions'] > 0:
            print("   ❌ CRITICAL REGRESSIONS DETECTED!")
            print("   Performance has degraded significantly.")
        elif regression_tests['total_regressions'] > 0:
            print("   ⚠️  Minor regressions detected.")
            print("   Performance monitoring recommended.")
        else:
            print("   ✅ No regressions detected.")
            print("   Performance is stable or improved.")

        # Memory profiling summary
        if 'memory_profiles' in self.results:
            print(f"\n🧠 MEMORY PROFILING:")
            for scenario, profile in self.results['memory_profiles'].items():
                memory_stats = profile['memory_stats']
                print(f"   {scenario}: {memory_stats['mean']:.1f}MB avg, {memory_stats['max']:.1f}MB peak")

        # Performance verdict
        print(f"\n🎯 PERFORMANCE VERDICT:")
        if overall['critical_regressions'] > 0:
            print("   ❌ PERFORMANCE DEGRADED - Immediate attention required")
        elif overall['regressions_detected'] > 3:
            print("   ⚠️  PERFORMANCE CONCERNS - Review and optimize")
        else:
            print("   ✅ PERFORMANCE ACCEPTABLE - System is performing well")

        print("=" * 80)

    def save_results(self):
        """Save benchmark results to files."""
        # Save detailed results
        results_file = os.path.join(os.path.dirname(__file__), 'performance_benchmark_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Update baseline if performance improved
        if self.results['regression_tests']['critical_regressions'] == 0:
            self.update_baseline_metrics()

        print(f"📊 Performance results saved to: {results_file}")

    def update_baseline_metrics(self):
        """Update baseline metrics with current performance."""
        new_baseline = {}

        # Extract current performance as new baseline
        benchmarks = self.results['benchmarks']

        # Content detection baselines
        if 'content_detection' in benchmarks:
            for scenario, benchmark in benchmarks['content_detection'].items():
                if 'execution_time' in benchmark:
                    key = f"content_detection_{scenario.split('_')[0]}"
                    new_baseline[key] = {
                        'max_time': benchmark['execution_time'] * 1.2,  # 20% buffer
                        'max_memory': benchmark['memory_used'] * 1.2
                    }

        # Style analysis baselines
        if 'style_analysis' in benchmarks:
            for scenario, benchmark in benchmarks['style_analysis'].items():
                if 'execution_time' in benchmark:
                    key = f"style_analysis_{scenario.split('_')[0]}"
                    new_baseline[key] = {
                        'max_time': benchmark['execution_time'] * 1.2,
                        'max_memory': benchmark['memory_used'] * 1.2
                    }

        # End-to-end baseline
        if 'end_to_end_workflow' in benchmarks:
            benchmark = benchmarks['end_to_end_workflow']
            if 'execution_time' in benchmark:
                new_baseline['end_to_end_workflow'] = {
                    'max_time': benchmark['execution_time'] * 1.2,
                    'max_memory': benchmark['memory_used'] * 1.2
                }

        # Save updated baseline
        baseline_file = os.path.join(os.path.dirname(__file__), 'performance_baseline.json')
        with open(baseline_file, 'w') as f:
            json.dump(new_baseline, f, indent=2)

        print(f"📈 Baseline metrics updated: {baseline_file}")


def main():
    """Run performance benchmarks."""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()

    # Return appropriate exit code
    if results['overall']['critical_regressions'] > 0:
        print("❌ Critical performance regressions detected!")
        return 1
    elif results['overall']['regressions_detected'] > 3:
        print("⚠️  Multiple performance regressions detected!")
        return 1
    else:
        print("✅ Performance benchmarks completed successfully!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)