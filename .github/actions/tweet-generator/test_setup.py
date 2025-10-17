#!/usr/bin/env python3
"""
Simple test script to verify the project structure and core interfaces are working.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all core modules can be imported."""
    try:
        from models import (
            BlogPost, StyleProfile, ThreadData, Tweet, GeneratorConfig,
            EngagementLevel, HookType, ValidationStatus
        )
        from config import ConfigManager
        from exceptions import TweetGeneratorError
        from utils import ensure_directory, safe_filename
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_data_models():
    """Test that data models can be instantiated."""
    try:
        from models import BlogPost, GeneratorConfig, Tweet, StyleProfile

        # Test BlogPost
        post = BlogPost(
            file_path="_posts/2023-01-01-test.md",
            title="Test Post",
            content="Test content",
            frontmatter={"title": "Test"},
            canonical_url="https://example.com/test"
        )
        assert post.slug == "2023-01-01-test"

        # Test GeneratorConfig
        config = GeneratorConfig()
        validation = config.validate()
        assert validation.status in ["valid", "warning", "error"]

        # Test Tweet
        tweet = Tweet(content="Test tweet content")
        assert tweet.character_count == len("Test tweet content")

        # Test StyleProfile
        profile = StyleProfile()
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)

        print("✓ Data models working correctly")
        return True
    except Exception as e:
        print(f"✗ Data model test failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    try:
        from config import ConfigManager
        from models import ValidationStatus

        # Test environment validation
        env_result = ConfigManager.validate_environment()
        assert env_result.status in [ValidationStatus.VALID, ValidationStatus.WARNING, ValidationStatus.ERROR]

        # Test config loading
        config = ConfigManager.load_config()
        assert config.openrouter_model is not None

        print("✓ Configuration management working")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    try:
        from utils import safe_filename, truncate_text, count_words

        # Test safe filename
        safe_name = safe_filename("test file/name.md")
        assert "/" not in safe_name

        # Test text truncation
        truncated = truncate_text("This is a long text", 10, "...")
        assert len(truncated) <= 10

        # Test word counting
        word_count = count_words("This is a test")
        assert word_count == 4

        print("✓ Utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Utilities test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing GitHub Action Tweet Thread Generator setup...")
    print()

    tests = [
        test_imports,
        test_data_models,
        test_configuration,
        test_utilities
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Project structure is set up correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())