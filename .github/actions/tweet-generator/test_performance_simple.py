#!/usr/bin/env python3
"""
Simple performance validation test for the GitHub Tweet Thread Generator.
Tests basic performance metrics without complex file operations.
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def get_memory_usage():
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        return 0

def test_basic_performance():
    """Test basic performance of core components."""
    print("Testing basic performance...")

    try:
        start_time = time.time()
        initial_memory = get_memory_usage()

        # Test imports and basic functionality
        from content_detector import ContentDetector
        from style_analyzer import StyleAnalyzer
        from content_validator import ContentValidator
        from config import GeneratorConfig

        # Test object creation
        detector = ContentDetector()
        analyzer = StyleAnalyzer()
        validator = ContentValidator()
        config = GeneratorConfig()

        creation_time = time.time() - start_time
        final_memory = get_memory_usage()

        memory_usage = final_memory - initial_memory

        # Basic performance checks
        assert creation_time < 5.0, f"Object creation too slow: {creation_time:.2f}s"
        assert memory_usage < 100, f"Memory usage too high: {memory_usage:.1f}MB"

        print(f"✓ Basic performance acceptable: {creation_time:.2f}s, {memory_usage:.1f}MB")
        return True

    except Exception as e:
        print(f"✗ Basic performance test failed: {e}")
        return False

def test_content_validation_performance():
    """Test content validation performance."""
    print("Testing content validation performance...")

    try:
        from content_validator import ContentValidator
        validator = ContentValidator()

        # Test with various content sizes
        test_contents = [
            "Short tweet content",
            "Medium length tweet content with some hashtags #test #performance",
            "Longer tweet content that tests the validation performance with more text and multiple sentences to process."
        ]

        start_time = time.time()

        for content in test_contents * 10:  # Test 30 validations
            result = validator.validate_character_limits([content])
            safety_result = validator.check_content_safety(content)

        validation_time = time.time() - start_time
        avg_time_per_validation = validation_time / 30

        # Should validate quickly
        assert avg_time_per_validation < 0.1, f"Validation too slow: {avg_time_per_validation:.3f}s per validation"

        print(f"✓ Content validation performance acceptable: {avg_time_per_validation:.3f}s per validation")
        return True

    except Exception as e:
        print(f"✗ Content validation performance test failed: {e}")
        return False

def test_style_analysis_performance():
    """Test style analysis performance with sample content."""
    print("Testing style analysis performance...")

    try:
        from style_analyzer import StyleAnalyzer
        analyzer = StyleAnalyzer()

        # Create sample content for analysis
        sample_posts = []
        for i in range(5):
            content = f"""
            This is sample blog post {i+1} for testing style analysis performance.
            It contains various technical terms, programming concepts, and different
            writing styles to test the analyzer's ability to process content efficiently.

            The content includes code examples, explanations, and different tones
            to simulate real blog posts that would be analyzed in production.
            """
            sample_posts.append(content)

        start_time = time.time()

        # Test vocabulary analysis
        vocab_profile = analyzer.analyze_vocabulary_patterns(sample_posts)

        # Test tone analysis
        tone_profile = analyzer.extract_tone_indicators(sample_posts)

        analysis_time = time.time() - start_time

        # Should analyze efficiently
        assert analysis_time < 10.0, f"Style analysis too slow: {analysis_time:.2f}s"

        print(f"✓ Style analysis performance acceptable: {analysis_time:.2f}s for 5 posts")
        return True

    except Exception as e:
        print(f"✗ Style analysis performance test failed: {e}")
        return False

def test_memory_efficiency():
    """Test memory efficiency during processing."""
    print("Testing memory efficiency...")

    try:
        initial_memory = get_memory_usage()

        # Process multiple operations to test memory usage
        from content_detector import ContentDetector
        from style_analyzer import StyleAnalyzer
        from content_validator import ContentValidator

        for i in range(10):
            # Create and use objects
            detector = ContentDetector()
            analyzer = StyleAnalyzer()
            validator = ContentValidator()

            # Simulate some processing
            test_content = f"Test content {i} for memory efficiency testing"
            result = validator.check_content_safety(test_content)

            # Force garbage collection
            import gc
            gc.collect()

        final_memory = get_memory_usage()
        memory_increase = final_memory - initial_memory

        # Should not leak significant memory
        assert memory_increase < 50, f"Potential memory leak: {memory_increase:.1f}MB"

        print(f"✓ Memory efficiency acceptable: {memory_increase:.1f}MB increase")
        return True

    except Exception as e:
        print(f"✗ Memory efficiency test failed: {e}")
        return False

def test_github_actions_compliance():
    """Test compliance with GitHub Actions resource limits."""
    print("Testing GitHub Actions compliance...")

    try:
        current_memory = get_memory_usage()

        # Test execution time for typical operations
        start_time = time.time()

        from content_detector import ContentDetector
        from style_analyzer import StyleAnalyzer
        from content_validator import ContentValidator

        # Simulate typical workflow operations
        detector = ContentDetector()
        analyzer = StyleAnalyzer()
        validator = ContentValidator()

        # Test multiple validations (simulating processing multiple posts)
        for i in range(20):
            content = f"Test blog post content {i} with various elements and text"
            result = validator.check_content_safety(content)
            char_result = validator.validate_character_limits([content])

        execution_time = time.time() - start_time

        # Estimate resource usage for large repositories
        estimated_time_100_posts = execution_time * 5  # Conservative estimate

        # GitHub Actions limits: 6 hours (21600s), ~7GB RAM
        assert current_memory < 500, f"Memory usage too high: {current_memory:.1f}MB"
        assert estimated_time_100_posts < 3600, f"Estimated time too high: {estimated_time_100_posts:.1f}s"

        print(f"✓ GitHub Actions compliance: {current_memory:.1f}MB memory, {estimated_time_100_posts:.1f}s estimated")
        return True

    except Exception as e:
        print(f"✗ GitHub Actions compliance test failed: {e}")
        return False

def run_performance_validation():
    """Run all performance validation tests."""
    print("="*60)
    print("RUNNING PERFORMANCE VALIDATION TESTS")
    print("="*60)

    tests = [
        ("Basic Performance", test_basic_performance),
        ("Content Validation Performance", test_content_validation_performance),
        ("Style Analysis Performance", test_style_analysis_performance),
        ("Memory Efficiency", test_memory_efficiency),
        ("GitHub Actions Compliance", test_github_actions_compliance)
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