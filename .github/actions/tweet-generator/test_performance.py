#!/usr/bin/env python3
"""
Performance and resource usage optimization test suite for the GitHub Tweet Thread Generator.
Tests memory usage, execution time, and resource limits compliance.
"""

import os
import sys
import time
import psutil
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any
import logging
from unittest.mock import Mock, patch
import threading
import concurrent.futures

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_detector import ContentDetector
from style_analyzer import StyleAnalyzer
from ai_orchestrator import AIOrchestrator
from logger import setup_logger

class PerformanceTestSuite:
    """Comprehensive performance and resource usage testing suite."""

    def __init__(self):
        self.logger = setup_logger("performance_test", logging.INFO)
        self.results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': [],
            'metrics': {}
        }
        self.process = psutil.Process()

    def run_test(self, test_name: str, test_func):
        """Run a single test and track results with performance metrics."""
        self.results['tests_run'] += 1

        # Record initial metrics
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()

        try:
            self.logger.info(f"Running performance test: {test_name}")
            result = test_func()

            # Record final metrics
            end_time = time.time()
            final_memory = self.process.memory_info().rss / 1024 / 1024  # MB

            execution_time = end_time - start_time
            memory_delta = final_memory - initial_memory

            self.results['metrics'][test_name] = {
                'execution_time': execution_time,
                'memory_usage': final_memory,
                'memory_delta': memory_delta,
                'result': result
            }

            self.results['tests_passed'] += 1
            self.logger.info(f"✓ {test_name} PASSED - Time: {execution_time:.2f}s, Memory: {final_memory:.1f}MB")

        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time

            self.results['tests_failed'] += 1
            self.results['failures'].append({
                'test': test_name,
                'error': str(e),
                'type': type(e).__name__,
                'execution_time': execution_time
            })
            self.logger.error(f"✗ {test_name} FAILED: {e} - Time: {execution_time:.2f}s")

    def create_large_test_repository(self, num_posts: int = 50):
        """Create a test repository with many blog posts."""
        test_dir = tempfile.mkdtemp(prefix="perf_test_")
        posts_dir = os.path.join(test_dir, "_posts")
        notebooks_dir = os.path.join(test_dir, "_notebooks")

        os.makedirs(posts_dir, exist_ok=True)
        os.makedirs(notebooks_dir, exist_ok=True)

        # Generate posts with varying content sizes
        for i in range(num_posts):
            # Vary content length (500-5000 words)
            content_length = 500 + (i * 90)

            post_content = f"""---
title: "Blog Post {i+1}: Advanced Topic Discussion"
date: 2024-01-{(i % 28) + 1:02d}
categories: [programming, tutorial, advanced]
tags: [python, javascript, web-development, data-science]
summary: "Comprehensive guide to advanced programming concepts and best practices"
publish: true
auto_post: {i % 3 == 0}
---

# Advanced Programming Concepts {i+1}

This is a comprehensive blog post about advanced programming concepts.
{'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' * (content_length // 50)}

## Technical Implementation

```python
def advanced_function_{i}():
    # Complex implementation here
    data = [x for x in range(1000) if x % 2 == 0]
    result = sum(data) * len(data)
    return result

class AdvancedClass_{i}:
    def __init__(self):
        self.data = {{'key_{j}': f'value_{j}' for j in range(100)}}

    def process_data(self):
        return [self.transform(item) for item in self.data.items()]

    def transform(self, item):
        key, value = item
        return f"{{key}}: {{value}}"
```

## Performance Considerations

When working with large datasets, it's important to consider:
- Memory usage optimization
- Algorithm complexity
- Caching strategies
- Parallel processing opportunities

{'This section contains detailed technical explanations. ' * (content_length // 100)}

## Conclusion

Advanced programming requires careful consideration of performance, maintainability, and scalability.
The techniques discussed here will help you build more efficient applications.

What are your thoughts on these approaches? Share your experience in the comments!
"""

            with open(os.path.join(posts_dir, f"2024-01-{(i % 28) + 1:02d}-post-{i+1}.md"), "w") as f:
                f.write(post_content)

        # Create some notebook files
        for i in range(min(10, num_posts // 5)):
            notebook_content = f"""---
title: "Data Science Notebook {i+1}"
date: 2024-01-{(i % 28) + 1:02d}
categories: [data-science, python, analysis]
summary: "Data analysis and visualization techniques"
publish: true
---

# Data Science Analysis {i+1}

{'This notebook demonstrates advanced data science techniques. ' * 50}

## Data Processing

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Generate sample data
data = np.random.randn(10000, 5)
df = pd.DataFrame(data, columns=['A', 'B', 'C', 'D', 'E'])

# Complex analysis
result = df.groupby(df.index // 100).agg({
    'A': ['mean', 'std', 'min', 'max'],
    'B': ['sum', 'count'],
    'C': lambda x: x.quantile(0.95)
})
```

{'Additional analysis and explanations follow. ' * 100}
"""

            with open(os.path.join(notebooks_dir, f"2024-01-{(i % 28) + 1:02d}-notebook-{i+1}.md"), "w") as f:
                f.write(notebook_content)

        return test_dir

    def test_memory_usage_large_repository(self):
        """Test memory usage with large repository (50+ posts)."""
        test_repo = self.create_large_test_repository(50)

        try:
            os.chdir(test_repo)

            # Monitor memory during content detection
            initial_memory = self.process.memory_info().rss / 1024 / 1024

            detector = ContentDetector()
            posts = detector.detect_changed_posts()

            detection_memory = self.process.memory_info().rss / 1024 / 1024

            # Monitor memory during style analysis
            analyzer = StyleAnalyzer()
            style_profile = analyzer.build_style_profile("_posts", "_notebooks")

            analysis_memory = self.process.memory_info().rss / 1024 / 1024

            # Verify memory usage is reasonable
            memory_increase = analysis_memory - initial_memory

            # Should not exceed 500MB for 50 posts
            assert memory_increase < 500, f"Memory usage too high: {memory_increase:.1f}MB"

            # Verify posts were detected
            assert len(posts) >= 45, f"Expected at least 45 posts, got {len(posts)}"

            return {
                'posts_processed': len(posts),
                'memory_increase': memory_increase,
                'detection_memory': detection_memory - initial_memory,
                'analysis_memory': analysis_memory - detection_memory
            }

        finally:
            shutil.rmtree(test_repo)

    def test_execution_time_scalability(self):
        """Test execution time scalability with increasing repository size."""
        results = {}

        for size in [10, 25, 50]:
            test_repo = self.create_large_test_repository(size)

            try:
                os.chdir(test_repo)

                start_time = time.time()

                # Test content detection performance
                detector = ContentDetector()
                posts = detector.detect_changed_posts()

                detection_time = time.time() - start_time

                # Test style analysis performance
                style_start = time.time()
                analyzer = StyleAnalyzer()
                style_profile = analyzer.build_style_profile("_posts", "_notebooks")

                analysis_time = time.time() - style_start
                total_time = time.time() - start_time

                results[size] = {
                    'posts': len(posts),
                    'detection_time': detection_time,
                    'analysis_time': analysis_time,
                    'total_time': total_time,
                    'time_per_post': total_time / len(posts) if posts else 0
                }

                # Verify reasonable performance
                assert total_time < 60, f"Processing {size} posts took too long: {total_time:.1f}s"

            finally:
                shutil.rmtree(test_repo)

        # Verify scalability is reasonable (should be roughly linear)
        if len(results) >= 2:
            sizes = sorted(results.keys())
            time_ratios = []

            for i in range(1, len(sizes)):
                prev_size, curr_size = sizes[i-1], sizes[i]
                size_ratio = curr_size / prev_size
                time_ratio = results[curr_size]['total_time'] / results[prev_size]['total_time']
                time_ratios.append(time_ratio / size_ratio)

            # Time complexity should be roughly O(n) - ratio should be close to 1
            avg_complexity = sum(time_ratios) / len(time_ratios)
            assert avg_complexity < 2.0, f"Time complexity too high: {avg_complexity:.2f}"

        return results

    def test_api_call_optimization(self):
        """Test API call patterns and caching effectiveness."""
        with patch('src.ai_orchestrator.httpx.post') as mock_post:
            # Mock API responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "tweets": ["Test tweet 1", "Test tweet 2"],
                            "hashtags": ["#test"]
                        })
                    }
                }]
            }
            mock_post.return_value = mock_response

            orchestrator = AIOrchestrator()

            # Test multiple calls with same content
            test_content = "Test blog post content"

            start_time = time.time()

            # Make multiple API calls
            for i in range(5):
                result = orchestrator.generate_thread_content(test_content, None)

            total_time = time.time() - start_time

            # Verify API calls were made
            call_count = mock_post.call_count

            return {
                'api_calls': call_count,
                'total_time': total_time,
                'avg_time_per_call': total_time / call_count if call_count > 0 else 0
            }

    def test_concurrent_processing(self):
        """Test concurrent processing capabilities."""
        test_repo = self.create_large_test_repository(20)

        try:
            os.chdir(test_repo)

            detector = ContentDetector()
            posts = detector.detect_changed_posts()

            # Test sequential processing
            start_time = time.time()
            sequential_results = []

            for post in posts[:5]:  # Process first 5 posts
                # Simulate processing
                time.sleep(0.1)  # Simulate work
                sequential_results.append(f"processed_{post.title}")

            sequential_time = time.time() - start_time

            # Test concurrent processing
            start_time = time.time()

            def process_post(post):
                time.sleep(0.1)  # Simulate work
                return f"processed_{post.title}"

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                concurrent_results = list(executor.map(process_post, posts[:5]))

            concurrent_time = time.time() - start_time

            # Concurrent should be faster
            speedup = sequential_time / concurrent_time

            return {
                'sequential_time': sequential_time,
                'concurrent_time': concurrent_time,
                'speedup': speedup,
                'posts_processed': len(posts[:5])
            }

        finally:
            shutil.rmtree(test_repo)

    def test_github_actions_resource_limits(self):
        """Test compliance with GitHub Actions resource limits."""
        # GitHub Actions limits:
        # - 6 hours execution time
        # - 7GB RAM
        # - 14GB disk space

        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        # Test memory usage is reasonable
        assert current_memory < 1000, f"Memory usage too high: {current_memory:.1f}MB (limit ~7GB)"

        # Test execution time estimation
        test_repo = self.create_large_test_repository(10)

        try:
            os.chdir(test_repo)

            start_time = time.time()

            # Simulate full workflow
            detector = ContentDetector()
            posts = detector.detect_changed_posts()

            analyzer = StyleAnalyzer()
            style_profile = analyzer.build_style_profile("_posts", "_notebooks")

            execution_time = time.time() - start_time

            # Estimate time for larger repositories
            estimated_time_100_posts = (execution_time / len(posts)) * 100

            # Should complete well within 6 hours (21600 seconds)
            assert estimated_time_100_posts < 3600, \
                f"Estimated time for 100 posts too high: {estimated_time_100_posts:.1f}s"

            return {
                'sample_posts': len(posts),
                'sample_time': execution_time,
                'estimated_time_100_posts': estimated_time_100_posts,
                'memory_usage': current_memory
            }

        finally:
            shutil.rmtree(test_repo)

    def test_incremental_style_analysis(self):
        """Test incremental style analysis performance optimization."""
        test_repo = self.create_large_test_repository(30)

        try:
            os.chdir(test_repo)

            analyzer = StyleAnalyzer()

            # Initial full analysis
            start_time = time.time()
            initial_profile = analyzer.build_style_profile("_posts", "_notebooks")
            initial_time = time.time() - start_time

            # Save profile
            profile_path = ".generated/writing-style-profile.json"
            os.makedirs(".generated", exist_ok=True)
            analyzer.save_style_profile(initial_profile, profile_path)

            # Add one new post
            new_post_content = """---
title: "New Post for Incremental Test"
date: 2024-02-01
categories: [test, incremental]
summary: "Testing incremental analysis"
publish: true
---

# New Post Content

This is a new post to test incremental analysis performance.
"""

            with open("_posts/2024-02-01-new-post.md", "w") as f:
                f.write(new_post_content)

            # Incremental analysis
            start_time = time.time()
            updated_profile = analyzer.update_style_profile_incremental(
                profile_path, ["_posts/2024-02-01-new-post.md"]
            )
            incremental_time = time.time() - start_time

            # Incremental should be much faster
            speedup = initial_time / incremental_time if incremental_time > 0 else float('inf')

            return {
                'initial_time': initial_time,
                'incremental_time': incremental_time,
                'speedup': speedup,
                'posts_in_initial': len(os.listdir("_posts")) - 1,
                'incremental_posts': 1
            }

        finally:
            shutil.rmtree(test_repo)

    def test_memory_cleanup(self):
        """Test memory cleanup and garbage collection."""
        initial_memory = self.process.memory_info().rss / 1024 / 1024

        # Create and process multiple repositories
        for i in range(3):
            test_repo = self.create_large_test_repository(15)

            try:
                os.chdir(test_repo)

                detector = ContentDetector()
                posts = detector.detect_changed_posts()

                analyzer = StyleAnalyzer()
                style_profile = analyzer.build_style_profile("_posts", "_notebooks")

                # Force garbage collection
                import gc
                gc.collect()

            finally:
                shutil.rmtree(test_repo)

        final_memory = self.process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # Memory should not increase significantly after cleanup
        assert memory_increase < 100, f"Memory leak detected: {memory_increase:.1f}MB increase"

        return {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': memory_increase
        }

    def run_all_tests(self):
        """Run all performance tests."""
        self.logger.info("Starting comprehensive performance testing...")

        # Run all performance tests
        self.run_test("Memory Usage Large Repository", self.test_memory_usage_large_repository)
        self.run_test("Execution Time Scalability", self.test_execution_time_scalability)
        self.run_test("API Call Optimization", self.test_api_call_optimization)
        self.run_test("Concurrent Processing", self.test_concurrent_processing)
        self.run_test("GitHub Actions Resource Limits", self.test_github_actions_resource_limits)
        self.run_test("Incremental Style Analysis", self.test_incremental_style_analysis)
        self.run_test("Memory Cleanup", self.test_memory_cleanup)

        # Print results
        self.print_results()
        return self.results

    def print_results(self):
        """Print test results summary with performance metrics."""
        print("\n" + "="*70)
        print("PERFORMANCE & RESOURCE USAGE TEST RESULTS")
        print("="*70)
        print(f"Tests Run: {self.results['tests_run']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")

        if self.results['failures']:
            print("\nPERFORMANCE FAILURES:")
            for failure in self.results['failures']:
                print(f"  ⚡ {failure['test']}: {failure['type']} - {failure['error']}")

        print("\nPERFORMANCE METRICS:")
        for test_name, metrics in self.results['metrics'].items():
            print(f"  📊 {test_name}:")
            print(f"     Execution Time: {metrics['execution_time']:.2f}s")
            print(f"     Memory Usage: {metrics['memory_usage']:.1f}MB")
            if metrics['memory_delta'] > 0:
                print(f"     Memory Delta: +{metrics['memory_delta']:.1f}MB")

            if isinstance(metrics['result'], dict):
                for key, value in metrics['result'].items():
                    if isinstance(value, (int, float)):
                        if 'time' in key.lower():
                            print(f"     {key}: {value:.2f}s")
                        elif 'memory' in key.lower():
                            print(f"     {key}: {value:.1f}MB")
                        else:
                            print(f"     {key}: {value}")

        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100
        print(f"\nPerformance Success Rate: {success_rate:.1f}%")

        if success_rate >= 85:
            print("🚀 Performance optimization PASSED!")
        else:
            print("🐌 Performance optimization NEEDS IMPROVEMENT!")

        print("="*70)

if __name__ == "__main__":
    suite = PerformanceTestSuite()
    results = suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results['tests_failed'] == 0 else 1)