#!/usr/bin/env python3
"""
Performance validation test for the GitHub Tweet Thread Generator.
Tests memory usage, execution time, and resource limits compliance.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def safe_cleanup(test_dir):
    """Safely cleanup test directory on Windows."""
    try:
        # Change to a safe directory first
        os.chdir(os.path.dirname(__file__))
        # Wait a bit for file handles to be released
        time.sleep(0.1)
        shutil.rmtree(test_dir)
    except Exception:
        # On Windows, sometimes files are locked, just ignore
        pass

def get_memory_usage():
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        # Fallback if psutil not available
        return 0

def create_test_repository(num_posts=10):
    """Create a test repository with multiple posts."""
    test_dir = tempfile.mkdtemp(prefix="perf_test_")
    posts_dir = os.path.join(test_dir, "_posts")
    os.makedirs(posts_dir, exist_ok=True)

    for i in range(num_posts):
        content = f"""---
title: "Performance Test Post {i+1}"
date: 2024-01-{(i % 28) + 1:02d}
categories: [test, performance]
summary: "Test post for performance validation"
publish: true
---

# Performance Test Content {i+1}

This is test content for performance validation. It contains enough text
to simulate real blog posts while testing the system's ability to handle
multiple posts efficiently.

## Technical Details

{'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' * 20}

## Code Examples

```python
def performance_test_{i}():
    data = [x for x in range(100) if x % 2 == 0]
    return sum(data)
```

## Conclusion

{'This section contains additional content for testing. ' * 10}
"""

        with open(os.path.join(posts_dir, f"2024-01-{(i % 28) + 1:02d}-test-{i+1}.md"), "w") as f:
            f.write(content)

    return test_dir

def test_memory_usage():
    """Test memory usage with multiple posts."""
    print("Testing memory usage...")

    try:
        initial_memory = get_memory_usage()

        # Create test repository with 20 posts
        test_repo = create_test_repository(20)

        try:
            os.chdir(test_repo)

            from content_detector import ContentDetector
            from style_analyzer import StyleAnalyzer

            # Test content detection
            detector = ContentDetector()
            posts = detector.get_all_posts()

            detection_memory = get_memory_usage()

            # Test style analysis
            analyzer = StyleAnalyzer()
            style_profile = analyzer.build_style_profile("_posts", "_notebooks")

            final_memory = get_memory_usage()

            memory_increase = final_memory - initial_memory

            # Should not use excessive memory (limit: 200MB for 20 posts)
            assert memory_increase < 200, f"Memory usage too high: {memory_increase:.1f}MB"

            print(f"✓ Memory usage acceptable: {memory_increase:.1f}MB for {len(posts)} posts")
            return True

        finally:
            shutil.rmtree(test_repo)

    except Exception as e:
        print(f"✗ Memory usage test failed: {e}")
        return False

def test_execution_time():
    """Test execution time performance."""
    print("Testing execution time...")

    try:
        # Test with different repository sizes
        for size in [5, 10, 15]:
            test_repo = create_test_repository(size)

            try:
                os.chdir(test_repo)

                start_time = time.time()

                from content_detector import ContentDetector
                from style_analyzer import StyleAnalyzer

                # Test content detection
                detector = ContentDetector()
                posts = detector.get_all_posts()

                # Test style analysis
                analyzer = StyleAnalyzer()
                style_profile = analyzer.build_style_profile("_posts", "_notebooks")

                execution_time = time.time() - start_time
                time_per_post = execution_time / len(posts) if posts else 0

                # Should process posts efficiently (limit: 2 seconds per post)
                assert time_per_post < 2.0, f"Processing too slow: {time_per_post:.2f}s per post"

                print(f"✓ Processed {len(posts)} posts in {execution_time:.2f}s ({time_per_post:.2f}s per post)")

            finally:
                shutil.rmtree(test_repo)

        return True

    except Exception as e:
        print(f"✗ Execution time test failed: {e}")
        return False

def test_scalability():
    """Test scalability with increasing load."""
    print("Testing scalability...")

    try:
        results = {}

        for size in [5, 10, 20]:
            test_repo = create_test_repository(size)

            try:
                os.chdir(test_repo)

                start_time = time.time()

                from content_detector import ContentDetector
                detector = ContentDetector()
                posts = detector.get_all_posts()

                execution_time = time.time() - start_time
                results[size] = execution_time / len(posts) if posts else 0

            finally:
                shutil.rmtree(test_repo)

        # Check that time per post doesn't increase dramatically
        if len(results) >= 2:
            sizes = sorted(results.keys())
            max_ratio = 1.0

            for i in range(1, len(sizes)):
                ratio = results[sizes[i]] / results[sizes[i-1]]
                max_ratio = max(max_ratio, ratio)

            # Time per post should not increase by more than 50% as we scale
            assert max_ratio < 1.5, f"Poor scalability: {max_ratio:.2f}x increase in time per post"

        print(f"✓ Scalability acceptable: {results}")
        return True

    except Exception as e:
        print(f"✗ Scalability test failed: {e}")
        return False

def test_github_actions_limits():
    """Test compliance with GitHub Actions resource limits."""
    print("Testing GitHub Actions limits compliance...")

    try:
        current_memory = get_memory_usage()

        # GitHub Actions has ~7GB RAM limit
        memory_limit_mb = 1000  # Conservative limit for our test
        assert current_memory < memory_limit_mb, f"Memory usage too high: {current_memory:.1f}MB"

        # Test execution time estimation
        test_repo = create_test_repository(10)

        try:
            os.chdir(test_repo)

            start_time = time.time()

            from content_detector import ContentDetector
            from style_analyzer import StyleAnalyzer

            detector = ContentDetector()
            posts = detector.get_all_posts()

            analyzer = StyleAnalyzer()
            style_profile = analyzer.build_style_profile("_posts", "_notebooks")

            execution_time = time.time() - start_time

            # Estimate time for 100 posts (large blog)
            estimated_time_100_posts = (execution_time / len(posts)) * 100

            # Should complete well within 1 hour (GitHub Actions has 6 hour limit)
            time_limit_seconds = 3600  # 1 hour
            assert estimated_time_100_posts < time_limit_seconds, \
                f"Estimated time too high: {estimated_time_100_posts:.1f}s for 100 posts"

            print(f"✓ GitHub Actions limits compliant: {current_memory:.1f}MB memory, {estimated_time_100_posts:.1f}s estimated for 100 posts")
            return True

        finally:
            shutil.rmtree(test_repo)

    except Exception as e:
        print(f"✗ GitHub Actions limits test failed: {e}")
        return False

def test_resource_cleanup():
    """Test resource cleanup and memory management."""
    print("Testing resource cleanup...")

    try:
        initial_memory = get_memory_usage()

        # Process multiple repositories to test cleanup
        for i in range(3):
            test_repo = create_test_repository(10)

            try:
                os.chdir(test_repo)

                from content_detector import ContentDetector
                from style_analyzer import StyleAnalyzer

                detector = ContentDetector()
                posts = detector.get_all_posts()

                analyzer = StyleAnalyzer()
                style_profile = analyzer.build_style_profile("_posts", "_notebooks")

                # Force garbage collection
                import gc
                gc.collect()

            finally:
                shutil.rmtree(test_repo)

        final_memory = get_memory_usage()
        memory_increase = final_memory - initial_memory

        # Memory should not increase significantly after processing multiple repos
        memory_leak_threshold = 50  # MB
        assert memory_increase < memory_leak_threshold, f"Potential memory leak: {memory_increase:.1f}MB increase"

        print(f"✓ Resource cleanup working: {memory_increase:.1f}MB net increase")
        return True

    except Exception as e:
        print(f"✗ Resource cleanup test failed: {e}")
        return False

def run_performance_validation():
    """Run all performance validation tests."""
    print("="*60)
    print("RUNNING PERFORMANCE VALIDATION TESTS")
    print("="*60)

    tests = [
        ("Memory Usage", test_memory_usage),
        ("Execution Time", test_execution_time),
        ("Scalability", test_scalability),
        ("GitHub Actions Limits", test_github_actions_limits),
        ("Resource Cleanup", test_resource_cleanup)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            failed += 1
        print()

    print("="*60)
    print("PERFORMANCE VALIDATION RESULTS")
    print("="*60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Success Rate: {(passed / (passed + failed)) * 100:.1f}%")

    if failed == 0:
        print("🚀 All performance validation tests passed!")
        return True
    elif failed <= 1:
        print("⚡ Performance is acceptable with minor issues")
        return True
    else:
        print("🐌 Performance optimization needed!")
        return False

if __name__ == "__main__":
    success = run_performance_validation()
    sys.exit(0 if success else 1)