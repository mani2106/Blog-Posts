# Validation and Safety Tests

This document describes the comprehensive validation and safety test suite implemented for the GitHub Tweet Thread Generator.

## Overview

The test suite covers all aspects of content validation and safety as specified in task 6.4:
- Character limit enforcement with various content types
- Content safety filtering effectiveness
- Error handling and recovery scenarios
- JSON structure validation

## Test Coverage

### 1. Character Limit Validation (`TestCharacterLimitValidation`)

**Tests Implemented:**
- `test_basic_character_limit_enforcement` - Basic 280 character limit validation
- `test_character_limit_violations` - Detection of tweets exceeding limits
- `test_url_shortening_calculation` - Proper handling of URL shortening (t.co links)
- `test_unicode_character_handling` - Unicode character counting (emojis, accented chars, etc.)
- `test_warning_threshold` - Warning when approaching character limit (90% threshold)
- `test_mixed_content_types` - Validation with mixed valid/invalid content
- `test_empty_and_edge_cases` - Edge cases like empty tweets
- `test_custom_character_limits` - Custom character limits for different platforms

**Key Features Tested:**
- URL shortening to 23 characters (Twitter t.co links)
- Unicode character proper counting
- Warning at 90% of character limit
- Multiple URL handling
- Complex emoji sequences

### 2. Content Safety Filtering (`TestContentSafetyFiltering`)

**Tests Implemented:**
- `test_profanity_detection` - Detection of profane language
- `test_hate_speech_detection` - Detection of harmful/hate speech content
- `test_spam_detection` - Detection of spam and promotional content
- `test_safe_content_passes` - Verification that safe content passes
- `test_numeric_claims_flagging` - Flagging of numeric claims needing verification
- `test_content_sanitization` - Content sanitization functionality
- `test_safety_scoring` - Safety scoring system validation
- `test_url_safety_checking` - Detection of suspicious URLs

**Safety Patterns Tested:**
- Profanity patterns (mild and strong)
- Hate speech keywords
- Spam indicators (buy now, make money, etc.)
- Suspicious URL patterns (bit.ly, tinyurl, etc.)
- Excessive capitalization detection
- Repetitive character detection

### 3. JSON Structure Validation (`TestJSONStructureValidation`)

**Tests Implemented:**
- `test_valid_json_structure` - Validation of correct JSON structure
- `test_missing_required_fields` - Detection of missing required fields
- `test_incorrect_field_types` - Detection of incorrect field types
- `test_tweet_object_structure` - Validation of tweet object structure
- `test_mixed_tweet_formats` - Mixed string and object tweet formats
- `test_hashtag_format_validation` - Hashtag format validation
- `test_engagement_score_validation` - Engagement score range validation
- `test_empty_arrays_validation` - Handling of empty arrays
- `test_nested_structure_validation` - Complex nested structure validation

**JSON Schema Validated:**
```json
{
  "tweets": ["string" | {"content": "string", "position": int, ...}],
  "hook_variations": ["string"],
  "hashtags": ["string"],
  "engagement_score": float (0.0-1.0)
}
```

### 4. Error Handling and Recovery (`TestErrorHandlingAndRecovery`)

**Tests Implemented:**
- `test_malformed_input_handling` - Graceful handling of malformed input
- `test_extremely_long_content_handling` - Handling of very long content
- `test_special_character_handling` - Special characters and edge cases
- `test_concurrent_validation_handling` - Thread-safe validation
- `test_memory_usage_with_large_datasets` - Memory efficiency with large datasets
- `test_validation_with_corrupted_data` - Handling of corrupted data
- `test_recovery_from_validation_failures` - Recovery after failures
- `test_error_message_quality` - Quality of error messages

**Error Scenarios Tested:**
- Null/empty inputs
- Extremely long content (10,000+ characters)
- Control characters and special Unicode
- HTML/JS injection attempts
- SQL-like content
- Concurrent access patterns
- Corrupted JSON structures
- NaN and infinity values

### 5. Engagement Element Validation (`TestEngagementElementValidation`)

**Tests Implemented:**
- `test_emoji_validation` - Emoji usage validation
- `test_hashtag_validation` - Hashtag format and usage validation
- `test_thread_sequence_validation` - Thread numbering sequence validation
- `test_call_to_action_validation` - Call-to-action presence in final tweets
- `test_thread_continuity_indicators` - Thread continuity indicators
- `test_engagement_statistics` - Engagement statistics calculation

**Engagement Elements Tested:**
- Emoji placement and frequency
- Hashtag format (#valid vs invalid)
- Thread sequences (1/5, 2/5, etc.)
- Call-to-action phrases
- Thread indicators (🧵, 👇)
- Mention handling (@user)

## Requirements Coverage

### Requirement 7.1 (Content Quality and Platform Compliance)
✅ Character limit validation with URL shortening
✅ Unicode character handling
✅ Platform-specific compliance checking
✅ Engagement element validation

### Requirement 7.2 (Content Safety and Filtering)
✅ Profanity detection and filtering
✅ Hate speech detection
✅ Spam content identification
✅ Numeric claim flagging
✅ Content sanitization
✅ Safety scoring system

### Requirement 7.3 (Error Handling and Recovery)
✅ Graceful error handling
✅ Input validation and sanitization
✅ Recovery from validation failures
✅ Comprehensive error logging
✅ Thread-safe operations

## Running the Tests

### Standalone Execution
```bash
python test_validation_safety.py
```

### With pytest
```bash
pytest test_validation_safety.py -v
```

### Using Test Runner
```bash
python run_validation_tests.py
```

## Test Results

The test suite includes **39 comprehensive tests** covering:
- 8 character limit validation tests
- 8 content safety filtering tests
- 9 JSON structure validation tests
- 8 error handling and recovery tests
- 6 engagement element validation tests

All tests pass with 100% success rate, ensuring robust validation and safety measures.

## Test Data and Scenarios

### Character Limit Test Cases
- Valid tweets (under 280 chars)
- Over-limit tweets (300+ chars)
- URLs with shortening calculation
- Unicode characters and emojis
- Warning threshold (90% of limit)
- Mixed valid/invalid content

### Safety Test Cases
- Profanity: "damn", "hell", "shit", etc.
- Hate speech: violence, harassment keywords
- Spam: "buy now", "make money", "guaranteed"
- Safe content: programming tutorials, tips
- Numeric claims: "95% of developers", statistics

### JSON Structure Test Cases
- Valid complete structures
- Missing required fields
- Incorrect field types
- Tweet object vs string formats
- Nested structures with metadata

### Error Handling Test Cases
- Null/empty inputs
- Extremely long content (10K+ chars)
- Special characters and Unicode edge cases
- Concurrent validation requests
- Corrupted data structures

## Integration with Main System

The validation and safety tests integrate with the main tweet generator system through:

1. **ContentValidator Class** - Main validation engine
2. **ValidationResult/SafetyResult Models** - Structured result objects
3. **Error Handling System** - Graceful error recovery
4. **Logging Integration** - Comprehensive audit trail

The tests ensure that all validation and safety requirements are met before content is processed or posted to social media platforms.