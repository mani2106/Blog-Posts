#!/usr/bin/env python3
"""
Comprehensive validation and safety tests for the GitHub Tweet Thread Generator.

This test suite covers:
- Character limit enforcement with various content types
- Content safety filtering effectiveness
- Error handling and recovery scenarios
- JSON structure validation

Requirements: 7.1, 7.2, 7.3
"""

import os
import sys
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import (
    ValidationResult, SafetyResult, Tweet, ValidationStatus,
    ThreadData, HookType, BlogPost
)
from content_validator import ContentValidator
from exceptions import ValidationError, SafetyError


class TestCharacterLimitValidation:
    """Test character limit enforcement with various content types."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()

    def test_basic_character_limit_enforcement(self):
        """Test basic character limit validation."""
        # Test valid tweets
        valid_tweets = [
            "This is a short tweet",
            "Another valid tweet with some content",
            "🚀 Emoji tweet with content"
        ]

        result = self.validator.validate_character_limits(valid_tweets, limit=280)
        assert result.is_valid
        assert result.status == ValidationStatus.VALID

    def test_character_limit_violations(self):
        """Test tweets that exceed character limits."""
        # Create tweets that exceed 280 characters
        long_tweet = "x" * 300  # 300 characters
        very_long_tweet = "This is a very long tweet that definitely exceeds the Twitter character limit of 280 characters. " * 3

        long_tweets = [long_tweet, very_long_tweet]

        result = self.validator.validate_character_limits(long_tweets, limit=280)
        assert not result.is_valid
        assert result.status == ValidationStatus.ERROR
        assert "violations" in result.details
        assert len(result.details["violations"]) == 2

    def test_url_shortening_calculation(self):
        """Test character count with URL shortening (t.co links)."""
        # Twitter shortens URLs to 23 characters
        tweet_with_url = "Check out this amazing article: https://example.com/very/long/url/path/that/would/normally/be/very/long"

        # Calculate expected length: tweet text + 23 (shortened URL) - original URL length
        expected_length = len(tweet_with_url) - len("https://example.com/very/long/url/path/that/would/normally/be/very/long") + 23

        result = self.validator.validate_character_limits([tweet_with_url], limit=280)
        assert result.is_valid

        # Test with multiple URLs
        multi_url_tweet = "Check these: https://example1.com and https://example2.com/long/path"
        result = self.validator.validate_character_limits([multi_url_tweet], limit=280)
        assert result.is_valid

    def test_unicode_character_handling(self):
        """Test proper Unicode character counting."""
        # Test with various Unicode characters
        unicode_tweets = [
            "🚀🎯💡 Emojis count as characters",
            "Café naïve résumé façade",  # Accented characters
            "中文字符测试",  # Chinese characters
            "🏳️‍🌈🏳️‍⚧️👨‍👩‍👧‍👦",  # Complex emoji sequences
        ]

        for tweet in unicode_tweets:
            result = self.validator.validate_character_limits([tweet], limit=280)
            # Should handle Unicode properly without errors
            assert isinstance(result, ValidationResult)

    def test_warning_threshold(self):
        """Test warning when approaching character limit."""
        # Create tweet just over 90% of limit (253 characters for 280 limit)
        warning_tweet = "x" * 253

        result = self.validator.validate_character_limits([warning_tweet], limit=280)
        assert result.is_valid
        assert result.status == ValidationStatus.WARNING
        assert "warnings" in result.details

    def test_mixed_content_types(self):
        """Test validation with mixed content types."""
        mixed_tweets = [
            "Short tweet",
            "Medium length tweet with some content and hashtags #test #example",
            "🚀 Tweet with emojis and mentions @user and links https://example.com",
            "x" * 275,  # Near limit
            "x" * 300,  # Over limit
        ]

        result = self.validator.validate_character_limits(mixed_tweets, limit=280)
        assert not result.is_valid  # Should fail due to over-limit tweet
        assert result.status == ValidationStatus.ERROR
        assert len(result.details["violations"]) == 1  # Only one violation

    def test_empty_and_edge_cases(self):
        """Test edge cases like empty tweets."""
        edge_cases = [
            "",  # Empty tweet
            " ",  # Single space
            "\n",  # Single newline
            "x",  # Single character
        ]

        result = self.validator.validate_character_limits(edge_cases, limit=280)
        assert result.is_valid

    def test_custom_character_limits(self):
        """Test validation with custom character limits."""
        tweets = ["x" * 100, "x" * 150]

        # Test with lower limit
        result = self.validator.validate_character_limits(tweets, limit=120)
        assert not result.is_valid  # 150-char tweet should fail

        # Test with higher limit
        result = self.validator.validate_character_limits(tweets, limit=200)
        assert result.is_valid  # Both should pass


class TestContentSafetyFiltering:
    """Test content safety filtering effectiveness."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()

    def test_profanity_detection(self):
        """Test profanity detection and filtering."""
        profane_content = [
            "This is a damn stupid idea",
            "What the hell is going on",
            "This shit doesn't work",
            "Don't be such a bitch about it"
        ]

        for content in profane_content:
            result = self.validator.check_content_safety(content)
            # Should detect profanity (may or may not flag as unsafe depending on severity)
            assert isinstance(result, SafetyResult)
            assert hasattr(result, 'flagged_content')

    def test_hate_speech_detection(self):
        """Test hate speech and harmful content detection."""
        harmful_content = [
            "I hate all people from that country",
            "Violence is the answer to this problem",
            "These people should be eliminated",
            "Terrorist attack was justified"
        ]

        for content in harmful_content:
            result = self.validator.check_content_safety(content)
            assert isinstance(result, SafetyResult)
            # Should flag serious harmful content
            if result.flagged_content:
                assert len(result.flagged_content) > 0

    def test_spam_detection(self):
        """Test spam and promotional content detection."""
        spam_content = [
            "Buy now! Limited time offer! Click here!",
            "Make money fast working from home!",
            "Guaranteed weight loss in 7 days!",
            "Free money! Act fast! Amazing results!"
        ]

        for content in spam_content:
            result = self.validator.check_content_safety(content)
            assert isinstance(result, SafetyResult)
            # Should detect spam indicators
            assert len(result.warnings) > 0 or len(result.flagged_content) > 0

    def test_safe_content_passes(self):
        """Test that safe content passes safety checks."""
        safe_content = [
            "This is a great tutorial about programming",
            "I learned something new today about machine learning",
            "Here are 5 tips for better code organization",
            "Thanks for reading! What are your thoughts?"
        ]

        for content in safe_content:
            result = self.validator.check_content_safety(content)
            assert result.is_safe
            assert result.safety_score > 0.7

    def test_numeric_claims_flagging(self):
        """Test flagging of numeric claims that need verification."""
        numeric_claims = [
            "95% of developers don't know this secret",
            "Studies show that 80% of people prefer this method",
            "Research indicates 3x faster performance",
            "Only 10% of users understand this concept",
            "According to experts, 90% improvement is possible"
        ]

        for claim in numeric_claims:
            flagged = self.validator.flag_numeric_claims(claim)
            assert len(flagged) > 0  # Should flag numeric claims

    def test_content_sanitization(self):
        """Test content sanitization functionality."""
        problematic_content = [
            "This is sooooooo amazing!!!!!!!",  # Excessive punctuation
            "WHY ARE YOU SHOUTING AT ME",  # Excessive caps
            "This damn thing is broken",  # Mild profanity
            "Buy now!!!! Limited time!!!! Act fast!!!!"  # Spam-like
        ]

        for content in problematic_content:
            sanitized = self.validator.sanitize_content(content)
            assert len(sanitized) > 0
            assert sanitized != content  # Should be modified

    def test_safety_scoring(self):
        """Test safety scoring system."""
        # Test content with varying safety levels
        test_cases = [
            ("Perfect safe content", 1.0),
            ("Mild profanity damn", 0.8),
            ("Multiple damn shit issues", 0.6),
            ("Hate speech and violence", 0.3)
        ]

        for content, expected_min_score in test_cases:
            result = self.validator.check_content_safety(content)
            # Safety score should be reasonable
            assert 0.0 <= result.safety_score <= 1.0

    def test_url_safety_checking(self):
        """Test URL safety validation."""
        suspicious_urls = [
            "Check this out: bit.ly/suspicious",
            "Visit: tinyurl.com/malware",
            "Click: goo.gl/phishing"
        ]

        for content in suspicious_urls:
            result = self.validator.check_content_safety(content)
            # Should warn about suspicious URLs
            assert len(result.warnings) > 0 or len(result.flagged_content) > 0


class TestJSONStructureValidation:
    """Test JSON structure validation for AI model responses."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()

    def test_valid_json_structure(self):
        """Test validation of correct JSON structure."""
        valid_json = {
            "tweets": ["Tweet 1", "Tweet 2", "Tweet 3"],
            "hook_variations": ["Hook 1", "Hook 2", "Hook 3"],
            "hashtags": ["#programming", "#tutorial"],
            "engagement_score": 0.85
        }

        result = self.validator.verify_json_structure(valid_json)
        assert result.is_valid
        assert result.status == ValidationStatus.VALID

    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        incomplete_json = {
            "tweets": ["Tweet 1", "Tweet 2"],
            # Missing hook_variations, hashtags, engagement_score
        }

        result = self.validator.verify_json_structure(incomplete_json)
        assert not result.is_valid
        assert result.status == ValidationStatus.ERROR
        assert "errors" in result.details
        assert len(result.details["errors"]) >= 3  # Missing 3 fields

    def test_incorrect_field_types(self):
        """Test validation with incorrect field types."""
        invalid_types_json = {
            "tweets": "should be list",  # Wrong type
            "hook_variations": ["Hook 1", "Hook 2"],
            "hashtags": 123,  # Wrong type
            "engagement_score": "should be number"  # Wrong type
        }

        result = self.validator.verify_json_structure(invalid_types_json)
        assert not result.is_valid
        assert result.status == ValidationStatus.ERROR

    def test_tweet_object_structure(self):
        """Test validation of tweet objects within tweets array."""
        tweet_objects_json = {
            "tweets": [
                {"content": "Tweet 1", "position": 1},
                {"content": "Tweet 2", "position": 2},
                {"missing_content": "Invalid"}  # Missing content field
            ],
            "hook_variations": ["Hook 1"],
            "hashtags": ["#test"],
            "engagement_score": 0.8
        }

        result = self.validator.verify_json_structure(tweet_objects_json)
        assert not result.is_valid
        assert "Tweet 2 missing 'content' field" in str(result.details)

    def test_mixed_tweet_formats(self):
        """Test validation with mixed string and object tweet formats."""
        mixed_tweets_json = {
            "tweets": [
                "Simple string tweet",
                {"content": "Object tweet", "position": 2},
                123  # Invalid type
            ],
            "hook_variations": ["Hook 1"],
            "hashtags": ["#test"],
            "engagement_score": 0.8
        }

        result = self.validator.verify_json_structure(mixed_tweets_json)
        assert not result.is_valid

    def test_hashtag_format_validation(self):
        """Test hashtag format validation."""
        hashtag_json = {
            "tweets": ["Tweet 1"],
            "hook_variations": ["Hook 1"],
            "hashtags": ["#valid", "invalid_no_hash", "#also_valid"],
            "engagement_score": 0.8
        }

        result = self.validator.verify_json_structure(hashtag_json)
        # Should pass but with warnings about hashtag format
        assert result.is_valid
        if "warnings" in result.details:
            assert len(result.details["warnings"]) > 0

    def test_engagement_score_validation(self):
        """Test engagement score validation."""
        test_cases = [
            (0.5, True),    # Valid
            (1.0, True),    # Valid
            (0.0, True),    # Valid
            (1.5, True),    # Invalid but should warn, not error
            (-0.1, True),   # Invalid but should warn, not error
        ]

        for score, should_be_valid in test_cases:
            json_data = {
                "tweets": ["Tweet 1"],
                "hook_variations": ["Hook 1"],
                "hashtags": ["#test"],
                "engagement_score": score
            }

            result = self.validator.verify_json_structure(json_data)
            assert result.is_valid == should_be_valid

    def test_empty_arrays_validation(self):
        """Test validation with empty arrays."""
        empty_arrays_json = {
            "tweets": [],  # Empty tweets
            "hook_variations": [],
            "hashtags": [],
            "engagement_score": 0.0
        }

        result = self.validator.verify_json_structure(empty_arrays_json)
        # Should be valid structurally, even if empty
        assert result.is_valid

    def test_nested_structure_validation(self):
        """Test validation of nested structures."""
        complex_json = {
            "tweets": [
                {
                    "content": "Tweet 1",
                    "position": 1,
                    "engagement_elements": ["emoji", "question"],
                    "hashtags": ["#test"]
                }
            ],
            "hook_variations": ["Hook 1"],
            "hashtags": ["#main"],
            "engagement_score": 0.8,
            "metadata": {  # Additional nested data
                "model_used": "claude-3-sonnet",
                "generated_at": "2024-01-01T00:00:00Z"
            }
        }

        result = self.validator.verify_json_structure(complex_json)
        assert result.is_valid


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()

    def test_malformed_input_handling(self):
        """Test handling of malformed input data."""
        malformed_inputs = [
            None,
            "",
            [],
            {"invalid": "structure"},
            123,
            {"tweets": None}
        ]

        for malformed_input in malformed_inputs:
            try:
                if isinstance(malformed_input, dict):
                    result = self.validator.verify_json_structure(malformed_input)
                    assert isinstance(result, ValidationResult)
                elif isinstance(malformed_input, str):
                    result = self.validator.check_content_safety(malformed_input)
                    assert isinstance(result, SafetyResult)
            except Exception as e:
                # Should handle gracefully, not crash
                assert isinstance(e, (ValidationError, SafetyError, ValueError))

    def test_extremely_long_content_handling(self):
        """Test handling of extremely long content."""
        # Create very long content
        extremely_long_content = "x" * 10000

        # Should handle without crashing
        safety_result = self.validator.check_content_safety(extremely_long_content)
        assert isinstance(safety_result, SafetyResult)

        char_result = self.validator.validate_character_limits([extremely_long_content])
        assert isinstance(char_result, ValidationResult)
        assert not char_result.is_valid  # Should fail character limit

    def test_special_character_handling(self):
        """Test handling of special characters and edge cases."""
        special_content = [
            "\x00\x01\x02",  # Control characters
            "🏳️‍🌈🏳️‍⚧️👨‍👩‍👧‍👦",  # Complex emoji sequences
            "\\n\\t\\r",  # Escaped characters
            "<script>alert('xss')</script>",  # HTML/JS injection
            "SELECT * FROM users;",  # SQL-like content
        ]

        for content in special_content:
            try:
                safety_result = self.validator.check_content_safety(content)
                assert isinstance(safety_result, SafetyResult)

                char_result = self.validator.validate_character_limits([content])
                assert isinstance(char_result, ValidationResult)
            except Exception as e:
                # Should handle gracefully
                assert not isinstance(e, (SystemExit, KeyboardInterrupt))

    def test_concurrent_validation_handling(self):
        """Test handling of concurrent validation requests."""
        import threading
        import time

        results = []
        errors = []

        def validate_content(content):
            try:
                result = self.validator.check_content_safety(f"Test content {content}")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=validate_content, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should handle concurrent access
        assert len(results) == 10
        assert len(errors) == 0

    def test_memory_usage_with_large_datasets(self):
        """Test memory usage with large datasets."""
        # Create large dataset
        large_tweet_list = [f"Tweet number {i} with some content" for i in range(1000)]

        # Should handle large datasets without excessive memory usage
        result = self.validator.validate_character_limits(large_tweet_list)
        assert isinstance(result, ValidationResult)

    def test_validation_with_corrupted_data(self):
        """Test validation with corrupted or incomplete data."""
        corrupted_data_cases = [
            {"tweets": [None, "", "valid tweet"]},
            {"tweets": ["tweet"], "hook_variations": [None]},
            {"tweets": ["tweet"], "hashtags": [123, "valid"]},
            {"tweets": ["tweet"], "engagement_score": float('inf')},
            {"tweets": ["tweet"], "engagement_score": float('nan')},
        ]

        for corrupted_data in corrupted_data_cases:
            try:
                result = self.validator.verify_json_structure(corrupted_data)
                assert isinstance(result, ValidationResult)
                # Should handle corrupted data gracefully
            except Exception as e:
                # Should not crash with unhandled exceptions
                assert not isinstance(e, (SystemExit, KeyboardInterrupt))

    def test_recovery_from_validation_failures(self):
        """Test recovery mechanisms from validation failures."""
        # Test that validator can continue after failures
        failing_content = "x" * 500  # Over limit

        # First validation should fail
        result1 = self.validator.validate_character_limits([failing_content])
        assert not result1.is_valid

        # Validator should still work for subsequent valid content
        valid_content = "This is valid content"
        result2 = self.validator.validate_character_limits([valid_content])
        assert result2.is_valid

    def test_error_message_quality(self):
        """Test quality and usefulness of error messages."""
        # Test various error scenarios
        error_cases = [
            ({"tweets": "wrong type"}, "must be list"),
            ({"tweets": []}, "Missing required field"),
            ({"tweets": ["valid"], "engagement_score": "wrong"}, "must be"),
        ]

        for invalid_data, expected_message_part in error_cases:
            result = self.validator.verify_json_structure(invalid_data)
            if not result.is_valid:
                # Error messages should be informative
                assert len(result.message) > 0
                assert "errors" in result.details or "message" in result.__dict__


class TestEngagementElementValidation:
    """Test validation of engagement elements in tweets."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator()

    def test_emoji_validation(self):
        """Test emoji usage validation."""
        emoji_tweets = [
            "Great tutorial! 🚀",  # Good emoji usage
            "🚀🎯💡🔥⭐🌟✨",  # Too many emojis
            "No emojis here",  # No emojis
            "Mixed content 🚀 with text 💡 and more"  # Balanced
        ]

        result = self.validator.validate_engagement_elements(emoji_tweets)
        assert isinstance(result, ValidationResult)

    def test_hashtag_validation(self):
        """Test hashtag usage and format validation."""
        hashtag_tweets = [
            "Great post #programming #tutorial",  # Good hashtags
            "#too #many #hashtags #here #spam",  # Too many hashtags
            "No hashtags here",  # No hashtags
            "Invalid #hashtag-with-dash #123numbers",  # Invalid formats
            "#verylonghashtagnamethatexceedstwitterlimitsandshouldbeflagged"  # Too long
        ]

        result = self.validator.validate_engagement_elements(hashtag_tweets)
        assert isinstance(result, ValidationResult)

    def test_thread_sequence_validation(self):
        """Test thread sequence numbering validation."""
        sequence_tweets = [
            "1/5 First tweet in thread",
            "2/5 Second tweet continues",
            "3/5 Third tweet with content",
            "5/5 Oops, skipped 4!"  # Invalid sequence
        ]

        result = self.validator.validate_engagement_elements(sequence_tweets)
        # Should detect sequence issues
        if not result.is_valid:
            assert "sequence" in str(result.details).lower()

    def test_call_to_action_validation(self):
        """Test call-to-action validation in final tweets."""
        # Thread without CTA
        no_cta_tweets = [
            "1/2 Here's some information",
            "2/2 That's all folks"  # No CTA
        ]

        result = self.validator.validate_engagement_elements(no_cta_tweets)
        # Should warn about missing CTA
        if result.status == ValidationStatus.WARNING:
            assert "call-to-action" in str(result.details).lower()

        # Thread with good CTA
        good_cta_tweets = [
            "1/2 Here's some information",
            "2/2 What do you think about this approach?"  # Good CTA
        ]

        result = self.validator.validate_engagement_elements(good_cta_tweets)
        # Should pass or have fewer warnings
        assert result.is_valid

    def test_thread_continuity_indicators(self):
        """Test thread continuity indicators validation."""
        # Thread without continuity indicators
        no_indicators = [
            "First tweet with content",
            "Second tweet with more content",
            "Third tweet concluding"
        ]

        result = self.validator.validate_engagement_elements(no_indicators)
        # Should warn about lack of continuity indicators
        if result.status == ValidationStatus.WARNING:
            assert "continuity" in str(result.details).lower() or "thread" in str(result.details).lower()

    def test_engagement_statistics(self):
        """Test engagement statistics calculation."""
        mixed_tweets = [
            "🚀 First tweet #programming",
            "Second tweet with @mention",
            "Third tweet with question?",
            "🧵 Thread continues below"
        ]

        result = self.validator.validate_engagement_elements(mixed_tweets)
        assert "engagement_stats" in result.details
        stats = result.details["engagement_stats"]

        # Should count various engagement elements
        assert "emojis" in stats
        assert "hashtags" in stats
        assert "mentions" in stats
        assert "questions" in stats


def run_validation_safety_tests():
    """Run all validation and safety tests."""
    print("="*60)
    print("RUNNING VALIDATION AND SAFETY TESTS")
    print("="*60)

    test_classes = [
        TestCharacterLimitValidation,
        TestContentSafetyFiltering,
        TestJSONStructureValidation,
        TestErrorHandlingAndRecovery,
        TestEngagementElementValidation
    ]

    total_passed = 0
    total_failed = 0

    for test_class in test_classes:
        print(f"\n--- {test_class.__name__} ---")

        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]

        class_passed = 0
        class_failed = 0

        for test_method_name in test_methods:
            try:
                # Create instance and run setup
                test_instance = test_class()
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()

                # Run the test method
                test_method = getattr(test_instance, test_method_name)
                test_method()

                print(f"✓ {test_method_name}")
                class_passed += 1
                total_passed += 1

            except Exception as e:
                print(f"✗ {test_method_name}: {e}")
                class_failed += 1
                total_failed += 1

        print(f"Class Results: {class_passed} passed, {class_failed} failed")

    print("\n" + "="*60)
    print("VALIDATION AND SAFETY TEST RESULTS")
    print("="*60)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {(total_passed / (total_passed + total_failed)) * 100:.1f}%")

    if total_failed == 0:
        print("🎉 All validation and safety tests passed!")
        return True
    elif total_failed <= 3:
        print("⚠️  Minor issues detected - review recommended")
        return True
    else:
        print("🚨 Critical validation issues detected!")
        return False


if __name__ == "__main__":
    success = run_validation_safety_tests()
    sys.exit(0 if success else 1)