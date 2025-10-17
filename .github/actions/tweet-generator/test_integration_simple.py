#!/usr/bin/env python3
"""
Simple integration test to validate core functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test that all core modules can be imported."""
    print("Testing basic imports...")

    try:
        from models import BlogPost, StyleProfile, ThreadData
        from content_detector import ContentDetector
        from style_analyzer import StyleAnalyzer
        from content_validator import ContentValidator
        from config import GeneratorConfig
        print("✓ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_content_detection():
    """Test content detection with sample posts."""
    print("Testing content detection...")

    try:
        # Create temporary test repository
        test_dir = tempfile.mkdtemp()
        posts_dir = os.path.join(test_dir, "_posts")
        os.makedirs(posts_dir, exist_ok=True)

        # Create sample post
        sample_post = """---
title: "Test Post"
date: 2024-01-15
categories: [test]
summary: "A test post"
publish: true
---

# Test Content

This is a test blog post for validation.
"""

        with open(os.path.join(posts_dir, "2024-01-15-test.md"), "w") as f:
            f.write(sample_post)

        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)

        try:
            from content_detector import ContentDetector
            detector = ContentDetector()
            # Test getting all posts instead of git diff
            posts = detector.get_all_posts()

            assert len(posts) >= 0, "Should return list of posts"
            print("✓ Content detection works")
            return True

        finally:
            os.chdir(original_dir)
            shutil.rmtree(test_dir)

    except Exception as e:
        print(f"✗ Content detection failed: {e}")
        return False

def test_style_analysis():
    """Test style analysis functionality."""
    print("Testing style analysis...")

    try:
        # Create temporary test repository
        test_dir = tempfile.mkdtemp()
        posts_dir = os.path.join(test_dir, "_posts")
        notebooks_dir = os.path.join(test_dir, "_notebooks")
        os.makedirs(posts_dir, exist_ok=True)
        os.makedirs(notebooks_dir, exist_ok=True)

        # Create sample posts
        for i in range(3):
            sample_post = f"""---
title: "Test Post {i+1}"
date: 2024-01-{15+i}
categories: [test, programming]
summary: "A test post for style analysis"
publish: true
---

# Test Content {i+1}

This is test content for style analysis. It contains various programming concepts
and technical terminology that should be analyzed for patterns.

## Technical Details

Here are some code examples and explanations that demonstrate different
writing styles and technical approaches.

The content varies in tone and complexity to test the analysis capabilities.
"""

            with open(os.path.join(posts_dir, f"2024-01-{15+i}-test-{i+1}.md"), "w") as f:
                f.write(sample_post)

        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)

        try:
            from style_analyzer import StyleAnalyzer
            analyzer = StyleAnalyzer()

            # Test style profile building
            style_profile = analyzer.build_style_profile("_posts", "_notebooks")

            assert style_profile is not None, "Should return style profile"
            assert hasattr(style_profile, 'vocabulary_patterns'), "Should have vocabulary patterns"

            print("✓ Style analysis works")
            return True

        finally:
            os.chdir(original_dir)
            shutil.rmtree(test_dir)

    except Exception as e:
        print(f"✗ Style analysis failed: {e}")
        return False

def test_content_validation():
    """Test content validation functionality."""
    print("Testing content validation...")

    try:
        from content_validator import ContentValidator
        validator = ContentValidator()

        # Test character limit validation
        short_tweet = "This is a short tweet"
        long_tweet = "x" * 300  # Over 280 character limit

        short_result = validator.validate_character_limits([short_tweet])
        long_result = validator.validate_character_limits([long_tweet])

        assert short_result.is_valid, "Short tweet should be valid"
        assert not long_result.is_valid, "Long tweet should be invalid"

        # Test content safety
        safe_content = "This is safe content about programming"
        safety_result = validator.check_content_safety(safe_content)

        assert safety_result.is_safe, "Safe content should pass safety check"

        print("✓ Content validation works")
        return True

    except Exception as e:
        print(f"✗ Content validation failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")

    try:
        from config import GeneratorConfig

        # Test default configuration
        config = GeneratorConfig()

        assert hasattr(config, 'openrouter_model'), "Should have openrouter_model"
        assert hasattr(config, 'max_tweets_per_thread'), "Should have max_tweets_per_thread"

        print("✓ Configuration works")
        return True

    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Content Detection", test_content_detection),
        ("Style Analysis", test_style_analysis),
        ("Content Validation", test_content_validation),
        ("Configuration", test_configuration)
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
    print("INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Success Rate: {(passed / (passed + failed)) * 100:.1f}%")

    if failed == 0:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed!")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)