"""
Content validation and safety for the Tweet Thread Generator.

This module ensures content quality, safety, and platform compliance
through comprehensive validation and filtering systems.
"""

from typing import List, Dict, Any, Optional, Set, Callable
import re
import json
import logging
import time
from urllib.parse import urlparse

from models import ValidationResult, SafetyResult, Tweet, ValidationStatus, ThreadData
from exceptions import ValidationError, SafetyError
from utils import validate_twitter_character_limit, extract_hashtags
from error_handler import ErrorHandler, ErrorContext, RecoveryResult


class ContentValidator:
    """Validates content quality, safety, and platform compliance."""

    def __init__(self):
        """Initialize content validator."""
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler()

        # Load profanity and safety patterns
        self.profanity_patterns = self._load_profanity_patterns()
        self.safety_keywords = self._load_safety_keywords()

        # Character limits for different platforms
        self.platform_limits = {
            "twitter": 280,
            "x": 280
        }

        # Required JSON structure for AI responses
        self.required_json_fields = {
            "tweets": list,
            "hook_variations": list,
            "hashtags": list,
            "engagement_score": (int, float)
        }

        # Engagement element patterns
        self.engagement_patterns = {
            "emoji": r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+',
            "hashtag": r'#\w+',
            "mention": r'@\w+',
            "question": r'\?',
            "exclamation": r'!',
            "number_sequence": r'\d+/\d+',
            "thread_indicator": r'🧵|thread|👇'
        }

        # Numeric claim patterns for fact-checking
        self.numeric_claim_patterns = [
            r'\d+%\s+of\s+people',
            r'\d+%\s+of\s+\w+',
            r'\d+\s+out\s+of\s+\d+',
            r'\d+x\s+more\s+likely',
            r'\d+x\s+faster',
            r'\d+\s+times\s+more',
            r'increases?\s+by\s+\d+%',
            r'reduces?\s+by\s+\d+%',
            r'up\s+to\s+\d+%',
            r'over\s+\d+%',
            r'studies?\s+show\s+\d+%'
        ]

    def _load_profanity_patterns(self) -> List[str]:
        """Load profanity patterns from configuration or use defaults."""
        # Basic profanity patterns - in production, this would load from a config file
        return [
            r'\b(damn|hell|crap|shit|fuck|bitch|ass|bastard)\b',
            r'\b(wtf|omfg|stfu)\b',
        ]

    def _load_safety_keywords(self) -> List[str]:
        """Load safety keywords from configuration or use defaults."""
        # Basic safety keywords - in production, this would load from a config file
        return [
            'hate', 'kill', 'die', 'murder', 'suicide', 'bomb', 'terrorist',
            'nazi', 'racist', 'sexist', 'homophobic', 'transphobic',
            'violence', 'abuse', 'harassment', 'threat', 'doxx'
        ]

    def _calculate_effective_tweet_length(self, tweet: str) -> int:
        """
        Calculate effective tweet length accounting for URL shortening.

        Twitter automatically shortens URLs to t.co links (23 characters).
        """
        # Find URLs in the tweet
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, tweet)

        # Calculate length with URL shortening
        effective_length = len(tweet)
        for url in urls:
            # Twitter shortens all URLs to 23 characters
            effective_length = effective_length - len(url) + 23

        return effective_length

    def validate_character_limits(self, tweets: List[str], limit: int = 280) -> ValidationResult:
        """
        Validate that all tweets meet character limit requirements.

        Accounts for URL shortening (t.co links are 23 characters) and
        ensures proper character counting for Unicode characters.

        Args:
            tweets: List of tweet content
            limit: Character limit per tweet

        Returns:
            ValidationResult with limit compliance status
        """
        violations = []
        warnings = []

        for i, tweet in enumerate(tweets):
            # Calculate effective character count
            effective_length = self._calculate_effective_tweet_length(tweet)

            # Allow a small buffer (5 characters) over the limit before treating as error
            if effective_length > limit + 5:
                violations.append({
                    "tweet_index": i,
                    "content": tweet[:50] + "..." if len(tweet) > 50 else tweet,
                    "length": effective_length,
                    "limit": limit,
                    "excess": effective_length - limit
                })
            elif effective_length > limit * 0.9:  # Warning at 90% of limit
                warnings.append({
                    "tweet_index": i,
                    "content": tweet[:50] + "..." if len(tweet) > 50 else tweet,
                    "length": effective_length,
                    "limit": limit,
                    "usage_percent": round((effective_length / limit) * 100, 1)
                })

        if violations:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Character limit exceeded in {len(violations)} tweet(s)",
                details={
                    "violations": violations,
                    "warnings": warnings,
                    "limit": limit
                },
                is_valid=False
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"{len(warnings)} tweet(s) approaching character limit",
                details={
                    "warnings": warnings,
                    "limit": limit
                },
                is_valid=True
            )
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="All tweets within character limits",
                details={"limit": limit, "max_length": max(len(tweet) for tweet in tweets) if tweets else 0}
            )

    def check_content_safety(self, content: str) -> SafetyResult:
        """
        Check content for safety and appropriateness.

        Args:
            content: Content to check

        Returns:
            SafetyResult with safety assessment
        """
        flagged_content = []
        warnings = []
        safety_score = 1.0

        content_lower = content.lower()

        # Check for profanity
        for pattern in self.profanity_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                flagged_content.extend([f"Profanity: {match}" for match in matches])
                safety_score -= 0.2 * len(matches)

        # Check for safety keywords (hate speech, violence, etc.)
        for keyword in self.safety_keywords:
            if keyword in content_lower:
                flagged_content.append(f"Safety concern: {keyword}")
                safety_score -= 0.3

        # Check for spam indicators
        spam_patterns = [
            r'(buy now|click here|limited time|act fast|urgent)',
            r'(make money|get rich|earn \$\d+)',
            r'(free money|guaranteed|100% success)',
            r'(weight loss|lose \d+ pounds)',
            r'(miracle cure|amazing results)',
        ]

        for pattern in spam_patterns:
            if re.search(pattern, content_lower):
                warnings.append(f"Potential spam indicator: {pattern}")
                safety_score -= 0.1

        # Check for excessive capitalization (shouting)
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.5:
            warnings.append(f"Excessive capitalization ({caps_ratio:.1%}) - may appear as shouting")
            safety_score -= 0.1

        # Check for repetitive characters (spam indicator)
        if re.search(r'(.)\1{4,}', content):
            warnings.append("Repetitive characters detected")
            safety_score -= 0.1

        # Check for suspicious URLs
        suspicious_url_patterns = [
            r'bit\.ly',
            r'tinyurl',
            r'goo\.gl',
            r't\.co/[a-zA-Z0-9]{10,}',  # Very long t.co URLs might be suspicious
        ]

        for pattern in suspicious_url_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Suspicious URL pattern: {pattern}")
                safety_score -= 0.05

        # Ensure safety score doesn't go below 0
        safety_score = max(0.0, safety_score)

        # Determine if content is safe
        is_safe = safety_score >= 0.7 and len(flagged_content) == 0

        return SafetyResult(
            is_safe=is_safe,
            flagged_content=flagged_content,
            safety_score=safety_score,
            warnings=warnings
        )

    def verify_json_structure(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Verify JSON structure meets API requirements for AI model responses.

        Args:
            data: JSON data to verify

        Returns:
            ValidationResult with structure validation status
        """
        errors = []
        warnings = []

        # Check required fields
        for field, expected_type in self.required_json_fields.items():
            if field not in data:
                errors.append(f"Missing required field: {field}")
                continue

            value = data[field]
            if isinstance(expected_type, tuple):
                # Multiple allowed types
                if not isinstance(value, expected_type):
                    errors.append(f"Field '{field}' must be one of {expected_type}, got {type(value).__name__}")
            else:
                # Single expected type
                if not isinstance(value, expected_type):
                    errors.append(f"Field '{field}' must be {expected_type.__name__}, got {type(value).__name__}")

        # Validate tweets structure if present
        if "tweets" in data and isinstance(data["tweets"], list):
            for i, tweet in enumerate(data["tweets"]):
                if isinstance(tweet, dict):
                    # Check tweet object structure
                    if "content" not in tweet:
                        errors.append(f"Tweet {i} missing 'content' field")
                    elif not isinstance(tweet["content"], str):
                        errors.append(f"Tweet {i} 'content' must be string")

                    # Optional fields validation
                    if "position" in tweet and not isinstance(tweet["position"], int):
                        warnings.append(f"Tweet {i} 'position' should be integer")

                elif isinstance(tweet, str):
                    # Simple string format is acceptable
                    continue
                else:
                    errors.append(f"Tweet {i} must be string or object with 'content' field")

        # Validate hook_variations if present
        if "hook_variations" in data and isinstance(data["hook_variations"], list):
            for i, hook in enumerate(data["hook_variations"]):
                if not isinstance(hook, str):
                    errors.append(f"Hook variation {i} must be string")

        # Validate hashtags if present
        if "hashtags" in data and isinstance(data["hashtags"], list):
            for i, hashtag in enumerate(data["hashtags"]):
                if not isinstance(hashtag, str):
                    errors.append(f"Hashtag {i} must be string")
                elif not hashtag.startswith('#') and hashtag:
                    warnings.append(f"Hashtag {i} should start with '#': {hashtag}")

        # Validate engagement_score if present
        if "engagement_score" in data:
            score = data["engagement_score"]
            if isinstance(score, (int, float)):
                if not (0 <= score <= 1):
                    warnings.append(f"Engagement score should be between 0 and 1, got {score}")

        if errors:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"JSON structure validation failed: {len(errors)} error(s)",
                details={"errors": errors, "warnings": warnings},
                is_valid=False
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"JSON structure has {len(warnings)} warning(s)",
                details={"warnings": warnings},
                is_valid=True
            )
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="JSON structure is valid",
                is_valid=True
            )

    def validate_engagement_elements(self, tweets: List[str]) -> ValidationResult:
        """
        Validate engagement elements are properly formatted and positioned.

        Args:
            tweets: List of tweet content

        Returns:
            ValidationResult with engagement validation status
        """
        issues = []
        warnings = []
        engagement_stats = {
            "emojis": 0,
            "hashtags": 0,
            "mentions": 0,
            "questions": 0,
            "thread_indicators": 0
        }

        for i, tweet in enumerate(tweets):
            tweet_issues = []

            # Check emoji usage
            emojis = re.findall(self.engagement_patterns["emoji"], tweet)
            engagement_stats["emojis"] += len(emojis)

            # Validate emoji placement (not too many consecutive)
            if len(emojis) > 5:
                tweet_issues.append(f"Too many emojis ({len(emojis)}) - may appear spammy")

            # Check hashtag usage and format
            hashtags = re.findall(self.engagement_patterns["hashtag"], tweet)
            engagement_stats["hashtags"] += len(hashtags)

            for hashtag in hashtags:
                # Validate hashtag format
                if not re.match(r'^#[a-zA-Z0-9_]+$', hashtag):
                    tweet_issues.append(f"Invalid hashtag format: {hashtag}")
                elif len(hashtag) > 100:  # Twitter hashtag limit
                    tweet_issues.append(f"Hashtag too long: {hashtag}")

            if len(hashtags) > 3:
                tweet_issues.append(f"Too many hashtags ({len(hashtags)}) - may reduce engagement")

            # Check mentions
            mentions = re.findall(self.engagement_patterns["mention"], tweet)
            engagement_stats["mentions"] += len(mentions)

            # Check for questions
            questions = re.findall(self.engagement_patterns["question"], tweet)
            engagement_stats["questions"] += len(questions)

            # Check thread indicators
            thread_indicators = re.findall(self.engagement_patterns["thread_indicator"], tweet, re.IGNORECASE)
            engagement_stats["thread_indicators"] += len(thread_indicators)

            # Check for number sequences (1/5, 2/5, etc.)
            number_sequences = re.findall(self.engagement_patterns["number_sequence"], tweet)
            if number_sequences:
                # Validate sequence format
                for seq in number_sequences:
                    current, total = map(int, seq.split('/'))
                    if current > total:
                        tweet_issues.append(f"Invalid sequence: {seq} (current > total)")
                    elif current == 0:
                        tweet_issues.append(f"Invalid sequence: {seq} (should start from 1)")

            # Check for proper call-to-action in final tweet
            if i == len(tweets) - 1:  # Last tweet
                has_cta = any(phrase in tweet.lower() for phrase in [
                    "what do you think", "share your", "let me know", "comment below",
                    "tag someone", "retweet if", "follow for more", "thoughts?"
                ])
                if not has_cta and len(tweets) > 1:
                    warnings.append(f"Final tweet lacks call-to-action for engagement")

            if tweet_issues:
                issues.append({
                    "tweet_index": i,
                    "content": tweet[:50] + "..." if len(tweet) > 50 else tweet,
                    "issues": tweet_issues
                })

        # Overall thread validation
        if len(tweets) > 1:
            # Check for thread continuity indicators
            if engagement_stats["thread_indicators"] == 0 and engagement_stats["questions"] == 0:
                warnings.append("Thread lacks continuity indicators (🧵, 👇, questions)")

            # Check for engagement distribution
            if engagement_stats["emojis"] == 0:
                warnings.append("Thread lacks emojis for visual engagement")

            if engagement_stats["hashtags"] == 0:
                warnings.append("Thread lacks hashtags for discoverability")

        if issues:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Engagement validation failed in {len(issues)} tweet(s)",
                details={
                    "issues": issues,
                    "warnings": warnings,
                    "engagement_stats": engagement_stats
                },
                is_valid=False
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Engagement validation has {len(warnings)} warning(s)",
                details={
                    "warnings": warnings,
                    "engagement_stats": engagement_stats
                },
                is_valid=True
            )
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="Engagement elements are properly formatted",
                details={"engagement_stats": engagement_stats}
            )

    def flag_numeric_claims(self, content: str) -> List[str]:
        """
        Flag numeric claims that may need fact-checking.

        Args:
            content: Content to analyze

        Returns:
            List of flagged numeric claims
        """
        flagged_claims = []

        for pattern in self.numeric_claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                flagged_claims.append({
                    "claim": match,
                    "pattern": pattern,
                    "context": self._extract_context(content, match),
                    "requires_verification": True
                })

        # Additional patterns for specific claim types
        additional_patterns = [
            (r'research shows? (that )?[\w\s]+ \d+%', "Research claim"),
            (r'according to (studies?|research|experts?)', "Authority claim"),
            (r'\d+ (million|billion|thousand) people', "Population statistic"),
            (r'increases? (by )?up to \d+%', "Percentage increase claim"),
            (r'reduces? (by )?up to \d+%', "Percentage reduction claim"),
            (r'\d+x (more|less|faster|slower)', "Multiplier claim"),
            (r'only \d+% of people know', "Knowledge statistic"),
            (r'\d+ out of \d+ (people|users|customers)', "Ratio statistic"),
        ]

        for pattern, claim_type in additional_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                flagged_claims.append({
                    "claim": match,
                    "type": claim_type,
                    "context": self._extract_context(content, match),
                    "requires_verification": True
                })

        return flagged_claims

    def sanitize_content(self, content: str) -> str:
        """
        Sanitize content by removing or replacing problematic elements.

        Args:
            content: Content to sanitize

        Returns:
            Sanitized content
        """
        sanitized = content

        # Remove excessive repetitive characters (keep max 3)
        sanitized = re.sub(r'(.)\1{3,}', r'\1\1\1', sanitized)

        # Replace mild profanity with asterisks (keep first and last letter)
        mild_profanity = ['damn', 'hell', 'crap']
        for word in mild_profanity:
            if len(word) > 2:
                replacement = word[0] + '*' * (len(word) - 2) + word[-1]
                sanitized = re.sub(rf'\b{word}\b', replacement, sanitized, flags=re.IGNORECASE)

        # Remove or replace stronger profanity completely
        strong_profanity = ['shit', 'fuck', 'bitch', 'ass', 'bastard']
        for word in strong_profanity:
            sanitized = re.sub(rf'\b{word}\b', '[removed]', sanitized, flags=re.IGNORECASE)

        # Clean up excessive punctuation
        sanitized = re.sub(r'[!]{3,}', '!!', sanitized)
        sanitized = re.sub(r'[?]{3,}', '??', sanitized)
        sanitized = re.sub(r'[.]{4,}', '...', sanitized)

        # Remove excessive capitalization (convert to sentence case)
        words = sanitized.split()
        cleaned_words = []
        for word in words:
            if len(word) > 3 and word.isupper() and not word.startswith('#') and not word.startswith('@'):
                # Convert to title case, but preserve hashtags and mentions
                cleaned_words.append(word.capitalize())
            else:
                cleaned_words.append(word)
        sanitized = ' '.join(cleaned_words)

        # Clean up whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # Remove suspicious patterns that might be spam
        spam_removals = [
            r'\b(click here|buy now|act fast|limited time offer)\b',
            r'\b(make \$\d+|earn money fast|get rich quick)\b',
            r'\b(miracle cure|amazing results|guaranteed success)\b',
        ]

        for pattern in spam_removals:
            sanitized = re.sub(pattern, '[promotional content removed]', sanitized, flags=re.IGNORECASE)

        return sanitized

    def validate_thread_structure(self, tweets: List[Tweet]) -> ValidationResult:
        """
        Validate overall thread structure and flow.

        Args:
            tweets: List of Tweet objects

        Returns:
            ValidationResult with structure validation status
        """
        if not tweets:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="Thread is empty",
                is_valid=False
            )

        issues = []
        warnings = []

        # Check thread length
        if len(tweets) > 25:  # Twitter's thread limit
            issues.append(f"Thread too long ({len(tweets)} tweets) - Twitter limit is 25")
        elif len(tweets) > 10:
            warnings.append(f"Long thread ({len(tweets)} tweets) - consider breaking into smaller threads")

        # Validate position sequence
        positions = [tweet.position for tweet in tweets if tweet.position > 0]
        if positions:
            expected_positions = list(range(1, len(positions) + 1))
            if positions != expected_positions:
                issues.append(f"Tweet positions not sequential: {positions}")

        # Check first tweet (hook)
        first_tweet = tweets[0]
        if len(first_tweet.content) < 50:
            warnings.append("First tweet is very short - may not be engaging enough")

        # Check for hook elements in first tweet
        hook_indicators = [
            r'\?',  # Questions
            r'!',   # Exclamations
            r'\d+\s+(ways?|tips?|secrets?|reasons?)',  # Numbered lists
            r'(here\'s|this is) (how|why|what)',  # Explanatory hooks
            r'(most people|everyone) (don\'t|doesn\'t) (know|realize)',  # Contrarian
            r'\d+%',  # Statistics
            r'(imagine|what if|picture this)',  # Scenario hooks
        ]

        has_hook = any(re.search(pattern, first_tweet.content, re.IGNORECASE)
                      for pattern in hook_indicators)
        if not has_hook:
            warnings.append("First tweet lacks strong hook elements")

        # Check last tweet (call-to-action)
        if len(tweets) > 1:
            last_tweet = tweets[-1]
            cta_patterns = [
                r'(what do you think|thoughts)\?',
                r'(share|tell me) (your|about)',
                r'(comment|reply) (below|with)',
                r'(follow|subscribe) for more',
                r'(retweet|rt) if',
                r'tag someone who',
                r'which (one|option)',
                r'have you (tried|experienced)'
            ]

            has_cta = any(re.search(pattern, last_tweet.content, re.IGNORECASE)
                         for pattern in cta_patterns)
            if not has_cta:
                warnings.append("Last tweet lacks call-to-action for engagement")

        # Check content flow and transitions
        for i in range(1, len(tweets)):
            current_tweet = tweets[i]
            prev_tweet = tweets[i-1]

            # Check for abrupt topic changes
            if len(current_tweet.content) > 100 and len(prev_tweet.content) > 100:
                # Simple check for transition words
                transition_words = [
                    'but', 'however', 'meanwhile', 'next', 'then', 'also',
                    'additionally', 'furthermore', 'moreover', 'therefore'
                ]

                has_transition = any(word in current_tweet.content.lower().split()[:10]
                                   for word in transition_words)

                if not has_transition and i < len(tweets) - 1:
                    # Only warn for middle tweets, not the last one
                    pass  # This might be too strict, so we'll skip for now

        # Check for engagement elements distribution
        total_engagement_elements = sum(len(tweet.engagement_elements) for tweet in tweets)
        if total_engagement_elements == 0:
            warnings.append("Thread lacks engagement elements (emojis, questions, etc.)")

        # Check hashtag distribution
        hashtag_tweets = sum(1 for tweet in tweets if tweet.hashtags)
        if hashtag_tweets == 0:
            warnings.append("Thread lacks hashtags for discoverability")
        elif hashtag_tweets > len(tweets) * 0.5:
            warnings.append("Too many tweets with hashtags - may appear spammy")

        if issues:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Thread structure validation failed: {len(issues)} issue(s)",
                details={
                    "issues": issues,
                    "warnings": warnings,
                    "thread_length": len(tweets),
                    "engagement_elements": total_engagement_elements
                },
                is_valid=False
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Thread structure has {len(warnings)} warning(s)",
                details={
                    "warnings": warnings,
                    "thread_length": len(tweets),
                    "engagement_elements": total_engagement_elements
                },
                is_valid=True
            )
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="Thread structure is valid",
                details={
                    "thread_length": len(tweets),
                    "engagement_elements": total_engagement_elements
                }
            )

    def check_platform_compliance(self, tweets: List[str], platform: str = "twitter") -> ValidationResult:
        """
        Check compliance with platform-specific requirements.

        Args:
            tweets: List of tweet content
            platform: Target platform

        Returns:
            ValidationResult with compliance status
        """
        platform = platform.lower()
        if platform not in self.platform_limits:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Unsupported platform: {platform}",
                is_valid=False
            )

        issues = []
        warnings = []
        limit = self.platform_limits[platform]

        # Check character limits
        char_validation = self.validate_character_limits(tweets, limit)
        if char_validation.status == ValidationStatus.ERROR:
            issues.extend(char_validation.details.get("violations", []))
        elif char_validation.status == ValidationStatus.WARNING:
            warnings.extend(char_validation.details.get("warnings", []))

        # Platform-specific validations
        if platform in ["twitter", "x"]:
            for i, tweet in enumerate(tweets):
                # Check for excessive hashtags (Twitter best practice: 1-2 per tweet)
                hashtags = extract_hashtags(tweet)
                if len(hashtags) > 3:
                    warnings.append({
                        "tweet_index": i,
                        "issue": f"Too many hashtags ({len(hashtags)}) - Twitter recommends 1-2",
                        "hashtags": hashtags
                    })

                # Check for excessive mentions (can trigger spam filters)
                mentions = re.findall(r'@\w+', tweet)
                if len(mentions) > 5:
                    warnings.append({
                        "tweet_index": i,
                        "issue": f"Too many mentions ({len(mentions)}) - may trigger spam filters"
                    })

                # Check for URL shortening considerations
                urls = re.findall(r'https?://\S+', tweet)
                if len(urls) > 2:
                    warnings.append({
                        "tweet_index": i,
                        "issue": f"Multiple URLs ({len(urls)}) - may reduce engagement"
                    })

                # Check for excessive capitalization
                caps_ratio = sum(1 for c in tweet if c.isupper()) / len(tweet) if tweet else 0
                if caps_ratio > 0.3:
                    warnings.append({
                        "tweet_index": i,
                        "issue": f"Excessive capitalization ({caps_ratio:.1%}) - may appear as shouting"
                    })

                # Check for repetitive characters (spam indicator)
                if re.search(r'(.)\1{4,}', tweet):  # 5+ consecutive same characters
                    issues.append({
                        "tweet_index": i,
                        "issue": "Repetitive characters detected - may be flagged as spam"
                    })

                # Check for suspicious patterns
                if re.search(r'(click here|buy now|limited time|act now)', tweet, re.IGNORECASE):
                    warnings.append({
                        "tweet_index": i,
                        "issue": "Contains promotional language - may reduce organic reach"
                    })

        # Check thread-specific compliance
        if len(tweets) > 1:
            # Ensure thread has proper numbering or continuation indicators
            has_numbering = any(re.search(r'\d+/\d+', tweet) for tweet in tweets)
            has_continuation = any(re.search(r'(thread|🧵|👇)', tweet, re.IGNORECASE) for tweet in tweets)

            if not has_numbering and not has_continuation:
                warnings.append({
                    "issue": "Thread lacks numbering or continuation indicators",
                    "suggestion": "Add 1/n numbering or thread indicators (🧵, 👇)"
                })

        if issues:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Platform compliance failed: {len(issues)} issue(s)",
                details={
                    "platform": platform,
                    "issues": issues,
                    "warnings": warnings,
                    "character_limit": limit
                },
                is_valid=False
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Platform compliance has {len(warnings)} warning(s)",
                details={
                    "platform": platform,
                    "warnings": warnings,
                    "character_limit": limit
                },
                is_valid=True
            )
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                message=f"Content complies with {platform} requirements",
                details={"platform": platform, "character_limit": limit}
            )

    def calculate_safety_score(self, content: str) -> float:
        """
        Calculate overall safety score for content.

        Args:
            content: Content to score

        Returns:
            Safety score between 0.0 (unsafe) and 1.0 (safe)
        """
        safety_result = self.check_content_safety(content)
        return safety_result.safety_score

    def get_safety_warnings(self, content: str) -> List[str]:
        """
        Get list of safety warnings for content.

        Args:
            content: Content to check

        Returns:
            List of warning messages
        """
        safety_result = self.check_content_safety(content)
        warnings = safety_result.warnings.copy()

        if safety_result.flagged_content:
            warnings.append(f"Content flagged for: {', '.join(safety_result.flagged_content)}")

        if safety_result.safety_score < 0.5:
            warnings.append("Content has low safety score - manual review recommended")

        return warnings

    def _extract_context(self, content: str, match: str, context_length: int = 50) -> str:
        """
        Extract context around a matched string.

        Args:
            content: Full content
            match: Matched string
            context_length: Characters to include before/after match

        Returns:
            Context string with match highlighted
        """
        match_index = content.lower().find(match.lower())
        if match_index == -1:
            return match

        start = max(0, match_index - context_length)
        end = min(len(content), match_index + len(match) + context_length)

        context = content[start:end]

        # Add ellipsis if we truncated
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."

        return context

    def validate_content_comprehensive(self, tweets: List[str]) -> ValidationResult:
        """
        Perform comprehensive validation including safety, structure, and compliance.

        Args:
            tweets: List of tweet content

        Returns:
            Comprehensive validation result
        """
        all_issues = []
        all_warnings = []
        overall_safe = True

        # Check each tweet for safety
        for i, tweet in enumerate(tweets):
            safety_result = self.check_content_safety(tweet)

            if not safety_result.is_safe:
                overall_safe = False
                all_issues.append({
                    "tweet_index": i,
                    "type": "safety",
                    "flagged_content": safety_result.flagged_content,
                    "safety_score": safety_result.safety_score
                })

            if safety_result.warnings:
                all_warnings.extend([
                    {"tweet_index": i, "type": "safety", "warning": warning}
                    for warning in safety_result.warnings
                ])

            # Check for numeric claims
            numeric_claims = self.flag_numeric_claims(tweet)
            if numeric_claims:
                all_warnings.extend([
                    {"tweet_index": i, "type": "fact_check", "claim": claim}
                    for claim in numeric_claims
                ])

        # Check character limits
        char_validation = self.validate_character_limits(tweets)
        if char_validation.status == ValidationStatus.ERROR:
            all_issues.extend([
                {"type": "character_limit", **issue}
                for issue in char_validation.details.get("violations", [])
            ])
        elif char_validation.status == ValidationStatus.WARNING:
            all_warnings.extend([
                {"type": "character_limit", **warning}
                for warning in char_validation.details.get("warnings", [])
            ])

        # Check engagement elements
        engagement_validation = self.validate_engagement_elements(tweets)
        if engagement_validation.status == ValidationStatus.ERROR:
            all_issues.extend([
                {"type": "engagement", **issue}
                for issue in engagement_validation.details.get("issues", [])
            ])
        elif engagement_validation.status == ValidationStatus.WARNING:
            all_warnings.extend([
                {"type": "engagement", "warning": warning}
                for warning in engagement_validation.details.get("warnings", [])
            ])

        # Check platform compliance
        compliance_validation = self.check_platform_compliance(tweets)
        if compliance_validation.status == ValidationStatus.ERROR:
            all_issues.extend([
                {"type": "compliance", **issue}
                for issue in compliance_validation.details.get("issues", [])
            ])
        elif compliance_validation.status == ValidationStatus.WARNING:
            all_warnings.extend([
                {"type": "compliance", **warning}
                for warning in compliance_validation.details.get("warnings", [])
            ])

        # Determine overall status
        if all_issues or not overall_safe:
            status = ValidationStatus.ERROR
            message = f"Comprehensive validation failed: {len(all_issues)} critical issue(s)"
        elif all_warnings:
            status = ValidationStatus.WARNING
            message = f"Comprehensive validation passed with {len(all_warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            message = "All validation checks passed"

        return ValidationResult(
            status=status,
            message=message,
            details={
                "issues": all_issues,
                "warnings": all_warnings,
                "overall_safe": overall_safe,
                "total_tweets": len(tweets)
            },
            is_valid=(status != ValidationStatus.ERROR)
        )

    def validate_with_recovery(self,
                              tweets: List[str],
                              recovery_callback: Optional[Callable] = None) -> ValidationResult:
        """
        Validate content with automatic error recovery.

        Args:
            tweets: List of tweet content
            recovery_callback: Optional callback for content regeneration

        Returns:
            ValidationResult with recovery information
        """
        context = ErrorContext(
            operation="content_validation",
            component="ContentValidator",
            input_data={"tweets": tweets},
            max_attempts=3
        )

        try:
            # Attempt comprehensive validation
            result = self.validate_content_comprehensive(tweets)

            # If validation fails and we have a recovery callback, try recovery
            if not result.is_valid and recovery_callback:
                self.logger.info("Validation failed, attempting content recovery")

                recovery_result = self.error_handler.handle_validation_error(
                    ValidationError(result.message),
                    context,
                    recovery_callback
                )

                if recovery_result.success and recovery_result.result_data:
                    # Re-validate recovered content
                    recovered_tweets = recovery_result.result_data.get("tweets", [])
                    if recovered_tweets:
                        result = self.validate_content_comprehensive(recovered_tweets)
                        result.details["recovery_applied"] = True
                        result.details["recovery_strategy"] = recovery_result.strategy_used.value

            return result

        except Exception as e:
            self.logger.error(f"Validation error: {e}")

            # Handle the error through error handler
            recovery_result = self.error_handler.handle_error(e, context, recovery_callback)

            if recovery_result.success:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    message=f"Validation recovered using {recovery_result.strategy_used.value}",
                    details={
                        "recovery_applied": True,
                        "recovery_strategy": recovery_result.strategy_used.value,
                        "original_error": str(e)
                    }
                )
            else:
                return ValidationResult(
                    status=ValidationStatus.ERROR,
                    message=f"Validation failed and recovery unsuccessful: {e}",
                    details={"original_error": str(e), "recovery_failed": True},
                    is_valid=False
                )

    def handle_validation_failure(self,
                                 validation_result: ValidationResult,
                                 original_content: List[str],
                                 regenerate_callback: Optional[Callable] = None) -> ValidationResult:
        """
        Handle validation failures with recovery strategies.

        Args:
            validation_result: Failed validation result
            original_content: Original content that failed validation
            regenerate_callback: Callback to regenerate content

        Returns:
            Updated validation result after recovery attempt
        """
        if validation_result.is_valid:
            return validation_result

        context = ErrorContext(
            operation="validation_recovery",
            component="ContentValidator",
            input_data={"original_content": original_content, "validation_result": validation_result.details}
        )

        # Determine recovery strategy based on validation issues
        issues = validation_result.details.get("issues", [])

        # Check if issues are recoverable
        recoverable_issues = []
        critical_issues = []

        for issue in issues:
            issue_type = issue.get("type", "unknown")

            if issue_type in ["character_limit", "engagement"]:
                recoverable_issues.append(issue)
            elif issue_type in ["safety", "compliance"]:
                critical_issues.append(issue)

        # If we have critical safety issues, skip recovery
        if critical_issues:
            self.logger.warning("Critical safety issues detected, skipping recovery")
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="Critical safety issues prevent recovery",
                details={
                    **validation_result.details,
                    "recovery_skipped": True,
                    "critical_issues": critical_issues
                },
                is_valid=False
            )

        # Try to recover from recoverable issues
        if recoverable_issues and regenerate_callback:
            try:
                self.logger.info(f"Attempting recovery for {len(recoverable_issues)} recoverable issues")

                # Create recovery parameters based on issues
                recovery_params = self._create_recovery_parameters(recoverable_issues)

                # Attempt regeneration with recovery parameters
                recovered_content = regenerate_callback(recovery_params)

                if recovered_content:
                    # Re-validate recovered content
                    new_validation = self.validate_content_comprehensive(
                        recovered_content.get("tweets", [])
                    )

                    new_validation.details["recovery_applied"] = True
                    new_validation.details["recovery_params"] = recovery_params
                    new_validation.details["original_issues"] = len(issues)

                    return new_validation

            except Exception as recovery_error:
                self.logger.error(f"Content recovery failed: {recovery_error}")

        # Recovery not possible or failed
        return ValidationResult(
            status=ValidationStatus.ERROR,
            message=f"Validation failed and recovery not possible: {validation_result.message}",
            details={
                **validation_result.details,
                "recovery_attempted": bool(regenerate_callback),
                "recovery_failed": True
            },
            is_valid=False
        )

    def auto_fix_content(self, tweets: List[str]) -> Dict[str, Any]:
        """
        Automatically fix common content issues.

        Args:
            tweets: List of tweet content with issues

        Returns:
            Dictionary with fixed content and applied fixes
        """
        fixed_tweets = []
        applied_fixes = []

        for i, tweet in enumerate(tweets):
            fixed_tweet = tweet
            tweet_fixes = []

            # Fix character limit issues
            if len(fixed_tweet) > 280:
                # Try to truncate intelligently
                fixed_tweet = self._intelligent_truncate(fixed_tweet, 280)
                tweet_fixes.append("truncated_for_length")

            # Fix excessive hashtags
            hashtags = extract_hashtags(fixed_tweet)
            if len(hashtags) > 2:
                # Keep only first 2 hashtags
                for hashtag in hashtags[2:]:
                    fixed_tweet = fixed_tweet.replace(f"#{hashtag}", "")
                tweet_fixes.append("reduced_hashtags")

            # Fix excessive capitalization
            if self._has_excessive_caps(fixed_tweet):
                fixed_tweet = self._fix_capitalization(fixed_tweet)
                tweet_fixes.append("fixed_capitalization")

            # Clean up whitespace
            fixed_tweet = re.sub(r'\s+', ' ', fixed_tweet).strip()

            # Sanitize content
            sanitized = self.sanitize_content(fixed_tweet)
            if sanitized != fixed_tweet:
                fixed_tweet = sanitized
                tweet_fixes.append("sanitized_content")

            fixed_tweets.append(fixed_tweet)
            if tweet_fixes:
                applied_fixes.append({
                    "tweet_index": i,
                    "fixes": tweet_fixes,
                    "original_length": len(tweet),
                    "fixed_length": len(fixed_tweet)
                })

        return {
            "tweets": fixed_tweets,
            "applied_fixes": applied_fixes,
            "fixes_count": len(applied_fixes)
        }

    def _create_recovery_parameters(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create recovery parameters based on validation issues."""
        recovery_params = {
            "engagement_level": "low",  # More conservative
            "max_tweets": 5,  # Shorter threads
            "character_limit_buffer": 50,  # Leave more room
            "hashtag_limit": 1,  # Fewer hashtags
            "emoji_limit": 2,  # Fewer emojis
        }

        # Adjust based on specific issues
        for issue in issues:
            issue_type = issue.get("type", "")

            if issue_type == "character_limit":
                recovery_params["character_limit_buffer"] = 80
                recovery_params["max_tweets"] = 3
            elif issue_type == "engagement":
                recovery_params["engagement_level"] = "minimal"
                recovery_params["hashtag_limit"] = 0
                recovery_params["emoji_limit"] = 1

        return recovery_params

    def _intelligent_truncate(self, text: str, max_length: int) -> str:
        """Intelligently truncate text while preserving meaning."""
        if len(text) <= max_length:
            return text

        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        if len(sentences) > 1:
            truncated = sentences[0] + '.'
            if len(truncated) <= max_length - 3:  # Leave room for ellipsis
                return truncated

        # Try to truncate at word boundaries
        words = text.split()
        truncated_words = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_length - 3:  # Leave room for ellipsis
                break
            truncated_words.append(word)
            current_length += len(word) + 1

        if truncated_words:
            return ' '.join(truncated_words) + '...'
        else:
            # Last resort: hard truncate
            return text[:max_length - 3] + '...'

    def _has_excessive_caps(self, text: str) -> bool:
        """Check if text has excessive capitalization."""
        if not text:
            return False

        caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        return caps_ratio > 0.3

    def _fix_capitalization(self, text: str) -> str:
        """Fix excessive capitalization."""
        words = text.split()
        fixed_words = []

        for word in words:
            # Skip hashtags, mentions, and URLs
            if word.startswith(('#', '@', 'http')):
                fixed_words.append(word)
            elif len(word) > 3 and word.isupper():
                # Convert to title case
                fixed_words.append(word.capitalize())
            else:
                fixed_words.append(word)

        return ' '.join(fixed_words)

    def create_validation_report(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """
        Create a comprehensive validation report.

        Args:
            validation_result: Validation result to report on

        Returns:
            Detailed validation report
        """
        report = {
            "status": validation_result.status.value,
            "is_valid": validation_result.is_valid,
            "message": validation_result.message,
            "timestamp": time.time(),
            "summary": {
                "total_issues": 0,
                "total_warnings": 0,
                "critical_issues": 0,
                "recoverable_issues": 0
            },
            "details": validation_result.details,
            "recommendations": []
        }

        # Analyze issues and warnings
        issues = validation_result.details.get("issues", [])
        warnings = validation_result.details.get("warnings", [])

        report["summary"]["total_issues"] = len(issues)
        report["summary"]["total_warnings"] = len(warnings)

        # Categorize issues
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type in ["safety", "compliance"]:
                report["summary"]["critical_issues"] += 1
            else:
                report["summary"]["recoverable_issues"] += 1

        # Generate recommendations
        if report["summary"]["critical_issues"] > 0:
            report["recommendations"].append(
                "Critical safety or compliance issues detected. Manual review required."
            )

        if report["summary"]["recoverable_issues"] > 0:
            report["recommendations"].append(
                "Content has recoverable issues. Consider regenerating with more conservative parameters."
            )

        if validation_result.details.get("recovery_applied"):
            report["recommendations"].append(
                f"Content was automatically recovered using {validation_result.details.get('recovery_strategy')} strategy."
            )

        return report

    def validate_thread(self, thread: 'ThreadData') -> ValidationResult:
        """
        Validate a complete thread data object.

        Args:
            thread: ThreadData object to validate

        Returns:
            ValidationResult with thread validation status
        """
        try:
            # Extract tweet content from ThreadData
            tweet_contents = [tweet.content for tweet in thread.tweets]

            if not tweet_contents:
                return ValidationResult(
                    status=ValidationStatus.ERROR,
                    message="Thread contains no tweets",
                    is_valid=False
                )

            # Perform comprehensive validation on tweet contents
            content_validation = self.validate_content_comprehensive(tweet_contents)

            # Validate thread structure using Tweet objects
            structure_validation = self.validate_thread_structure(thread.tweets)

            # Combine results
            all_issues = []
            all_warnings = []

            # Add content validation issues
            if content_validation.details:
                all_issues.extend(content_validation.details.get("issues", []))
                all_warnings.extend(content_validation.details.get("warnings", []))

            # Add structure validation issues
            if structure_validation.details:
                structure_issues = structure_validation.details.get("issues", [])
                structure_warnings = structure_validation.details.get("warnings", [])

                # Mark structure issues with type
                for issue in structure_issues:
                    if isinstance(issue, dict):
                        issue["type"] = "structure"
                    else:
                        # Convert string to dict
                        structure_issues[structure_issues.index(issue)] = {
                            "type": "structure",
                            "message": str(issue)
                        }
                for warning in structure_warnings:
                    if isinstance(warning, dict):
                        warning["type"] = "structure"
                    else:
                        # Convert string to dict
                        structure_warnings[structure_warnings.index(warning)] = {
                            "type": "structure",
                            "message": str(warning)
                        }

                all_issues.extend(structure_issues)
                all_warnings.extend(structure_warnings)

            # Determine overall status
            if all_issues or not content_validation.is_valid or not structure_validation.is_valid:
                status = ValidationStatus.ERROR
                message = f"Thread validation failed: {len(all_issues)} issue(s)"
            elif all_warnings:
                status = ValidationStatus.WARNING
                message = f"Thread validation passed with {len(all_warnings)} warning(s)"
            else:
                status = ValidationStatus.VALID
                message = "Thread validation passed"

            return ValidationResult(
                status=status,
                message=message,
                details={
                    "issues": all_issues,
                    "warnings": all_warnings,
                    "thread_metadata": {
                        "post_slug": thread.post_slug,
                        "tweet_count": len(thread.tweets),
                        "engagement_score": thread.engagement_score,
                        "model_used": thread.model_used,
                        "style_profile_version": thread.style_profile_version
                    },
                    "content_validation": content_validation.details,
                    "structure_validation": structure_validation.details
                },
                is_valid=(status != ValidationStatus.ERROR)
            )

        except Exception as e:
            self.logger.error(f"Thread validation error: {e}")
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Thread validation failed with error: {str(e)}",
                details={"error": str(e)},
                is_valid=False
            )