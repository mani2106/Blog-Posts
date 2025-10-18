"""
Core data models and interfaces for the Tweet Thread Generator.

This module defines all the data structures used throughout the system,
including blog posts, style profiles, thread data, and configuration schemas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json


class EngagementLevel(str, Enum):
    """Engagement optimization levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HookType(str, Enum):
    """Types of engagement hooks for tweet threads."""
    CURIOSITY = "curiosity"
    CONTRARIAN = "contrarian"
    STATISTIC = "statistic"
    STORY = "story"
    QUESTION = "question"
    VALUE_PROPOSITION = "value_proposition"


class ValidationStatus(str, Enum):
    """Validation result statuses."""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class BlogPost:
    """Represents a blog post with metadata and content."""
    file_path: str
    title: str
    content: str
    frontmatter: Dict[str, Any]
    canonical_url: str
    categories: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    auto_post: bool = False
    slug: str = ""

    def __post_init__(self):
        """Generate slug from file path if not provided."""
        if not self.slug:
            import os
            self.slug = os.path.splitext(os.path.basename(self.file_path))[0]


@dataclass
class VocabularyProfile:
    """Vocabulary patterns and word usage analysis."""
    common_words: List[str] = field(default_factory=list)
    technical_terms: List[str] = field(default_factory=list)
    word_frequency: Dict[str, int] = field(default_factory=dict)
    average_word_length: float = 0.0
    vocabulary_diversity: float = 0.0
    preferred_synonyms: Dict[str, str] = field(default_factory=dict)


@dataclass
class ToneProfile:
    """Tone and sentiment analysis results."""
    formality_level: float = 0.5  # 0.0 = very informal, 1.0 = very formal
    enthusiasm_level: float = 0.5  # 0.0 = subdued, 1.0 = very enthusiastic
    confidence_level: float = 0.5  # 0.0 = uncertain, 1.0 = very confident
    humor_usage: float = 0.0  # 0.0 = no humor, 1.0 = frequent humor
    personal_anecdotes: bool = False
    question_frequency: float = 0.0
    exclamation_frequency: float = 0.0


@dataclass
class StructureProfile:
    """Content structure and formatting preferences."""
    average_sentence_length: float = 0.0
    paragraph_length_preference: str = "medium"  # short, medium, long
    list_usage_frequency: float = 0.0
    code_block_frequency: float = 0.0
    header_usage_patterns: List[str] = field(default_factory=list)
    preferred_transitions: List[str] = field(default_factory=list)


@dataclass
class EmojiProfile:
    """Emoji usage patterns and preferences."""
    emoji_frequency: float = 0.0
    common_emojis: List[str] = field(default_factory=list)
    emoji_placement: str = "end"  # start, middle, end, mixed
    technical_emoji_usage: bool = False


@dataclass
class StyleProfile:
    """Comprehensive writing style analysis profile."""
    vocabulary_patterns: VocabularyProfile = field(default_factory=VocabularyProfile)
    tone_indicators: ToneProfile = field(default_factory=ToneProfile)
    content_structures: StructureProfile = field(default_factory=StructureProfile)
    emoji_usage: EmojiProfile = field(default_factory=EmojiProfile)
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    posts_analyzed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "vocabulary_patterns": {
                "common_words": self.vocabulary_patterns.common_words,
                "technical_terms": self.vocabulary_patterns.technical_terms,
                "word_frequency": self.vocabulary_patterns.word_frequency,
                "average_word_length": self.vocabulary_patterns.average_word_length,
                "vocabulary_diversity": self.vocabulary_patterns.vocabulary_diversity,
                "preferred_synonyms": self.vocabulary_patterns.preferred_synonyms
            },
            "tone_indicators": {
                "formality_level": self.tone_indicators.formality_level,
                "enthusiasm_level": self.tone_indicators.enthusiasm_level,
                "confidence_level": self.tone_indicators.confidence_level,
                "humor_usage": self.tone_indicators.humor_usage,
                "personal_anecdotes": self.tone_indicators.personal_anecdotes,
                "question_frequency": self.tone_indicators.question_frequency,
                "exclamation_frequency": self.tone_indicators.exclamation_frequency
            },
            "content_structures": {
                "average_sentence_length": self.content_structures.average_sentence_length,
                "paragraph_length_preference": self.content_structures.paragraph_length_preference,
                "list_usage_frequency": self.content_structures.list_usage_frequency,
                "code_block_frequency": self.content_structures.code_block_frequency,
                "header_usage_patterns": self.content_structures.header_usage_patterns,
                "preferred_transitions": self.content_structures.preferred_transitions
            },
            "emoji_usage": {
                "emoji_frequency": self.emoji_usage.emoji_frequency,
                "common_emojis": self.emoji_usage.common_emojis,
                "emoji_placement": self.emoji_usage.emoji_placement,
                "technical_emoji_usage": self.emoji_usage.technical_emoji_usage
            },
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "posts_analyzed": self.posts_analyzed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StyleProfile':
        """Create StyleProfile from dictionary."""
        vocab_data = data.get("vocabulary_patterns", {})
        tone_data = data.get("tone_indicators", {})
        structure_data = data.get("content_structures", {})
        emoji_data = data.get("emoji_usage", {})

        return cls(
            vocabulary_patterns=VocabularyProfile(**vocab_data),
            tone_indicators=ToneProfile(**tone_data),
            content_structures=StructureProfile(**structure_data),
            emoji_usage=EmojiProfile(**emoji_data),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            version=data.get("version", "1.0.0"),
            posts_analyzed=data.get("posts_analyzed", 0)
        )


@dataclass
class Tweet:
    """Individual tweet within a thread."""
    content: str
    character_count: int = 0
    engagement_elements: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    position: int = 0
    hook_type: Optional[HookType] = None

    def __post_init__(self):
        """Calculate character count if not provided."""
        if self.character_count == 0:
            self.character_count = len(self.content)


@dataclass
class ThreadPlan:
    """Plan for thread structure and content flow."""
    hook_type: HookType
    main_points: List[str] = field(default_factory=list)
    call_to_action: str = ""
    estimated_tweets: int = 0
    engagement_strategy: str = ""


@dataclass
class ThreadData:
    """Complete tweet thread with metadata."""
    post_slug: str
    tweets: List[Tweet] = field(default_factory=list)
    hook_variations: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    engagement_score: float = 0.0
    model_used: str = ""
    prompt_version: str = "1.0.0"
    generated_at: datetime = field(default_factory=datetime.now)
    style_profile_version: str = ""
    thread_plan: Optional[ThreadPlan] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "post_slug": self.post_slug,
            "tweets": [
                {
                    "content": tweet.content,
                    "character_count": tweet.character_count,
                    "engagement_elements": tweet.engagement_elements,
                    "hashtags": tweet.hashtags,
                    "position": tweet.position,
                    "hook_type": tweet.hook_type.value if tweet.hook_type else None
                }
                for tweet in self.tweets
            ],
            "hook_variations": self.hook_variations,
            "hashtags": self.hashtags,
            "engagement_score": self.engagement_score,
            "model_used": self.model_used,
            "prompt_version": self.prompt_version,
            "generated_at": self.generated_at.isoformat(),
            "style_profile_version": self.style_profile_version,
            "thread_plan": {
                "hook_type": self.thread_plan.hook_type.value,
                "main_points": self.thread_plan.main_points,
                "call_to_action": self.thread_plan.call_to_action,
                "estimated_tweets": self.thread_plan.estimated_tweets,
                "engagement_strategy": self.thread_plan.engagement_strategy
            } if self.thread_plan else None
        }


@dataclass
class ValidationResult:
    """Result of content validation."""
    status: ValidationStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True

    def __post_init__(self):
        """Set is_valid based on status."""
        self.is_valid = self.status != ValidationStatus.ERROR


@dataclass
class SafetyResult:
    """Result of content safety check."""
    is_safe: bool = True
    flagged_content: List[str] = field(default_factory=list)
    safety_score: float = 1.0
    warnings: List[str] = field(default_factory=list)


@dataclass
class PostResult:
    """Result of posting to social media platform."""
    success: bool = False
    tweet_ids: List[str] = field(default_factory=list)
    error_message: str = ""
    posted_at: datetime = field(default_factory=datetime.now)
    platform: str = "twitter"


@dataclass
class GeneratorConfig:
    """Configuration for the tweet thread generator."""
    # Model configuration
    openrouter_model: str = "z-ai/glm-4.5-air"
    creative_model: str = "z-ai/glm-4.5-air"
    verification_model: str = "z-ai/glm-4.5-air"

    # Thread configuration
    max_tweets_per_thread: int = 10
    hook_variations_count: int = 3
    engagement_optimization_level: EngagementLevel = EngagementLevel.HIGH

    # Posting configuration
    auto_post_enabled: bool = False
    dry_run_mode: bool = False

    # API configuration
    openrouter_api_key: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    github_token: str = ""

    # Directory configuration
    posts_directory: str = "_posts"
    notebooks_directory: str = "_notebooks"
    generated_directory: str = ".generated"
    posted_directory: str = ".posted"
    base_branch: str = "main"

    # Style analysis configuration
    min_posts_for_analysis: int = 3
    style_profile_version: str = "1.0.0"

    @classmethod
    def from_env(cls) -> 'GeneratorConfig':
        """Create configuration from environment variables."""
        import os

        return cls(
            openrouter_model=os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air"),
            creative_model=os.getenv("CREATIVE_MODEL", "z-ai/glm-4.5-air"),
            verification_model=os.getenv("VERIFICATION_MODEL", "z-ai/glm-4.5-air"),
            max_tweets_per_thread=int(os.getenv("MAX_TWEETS_PER_THREAD", "10")),
            hook_variations_count=int(os.getenv("HOOK_VARIATIONS_COUNT", "3")),
            engagement_optimization_level=EngagementLevel(os.getenv("ENGAGEMENT_LEVEL", "high")),
            auto_post_enabled=os.getenv("AUTO_POST_ENABLED", "false").lower() == "true",
            dry_run_mode=os.getenv("DRY_RUN", "false").lower() == "true",
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            twitter_api_key=os.getenv("TWITTER_API_KEY", ""),
            twitter_api_secret=os.getenv("TWITTER_API_SECRET", ""),
            twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
            twitter_access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
            github_token=os.getenv("GITHUB_TOKEN", ""),
            posts_directory=os.getenv("POSTS_DIRECTORY", "_posts"),
            notebooks_directory=os.getenv("NOTEBOOKS_DIRECTORY", "_notebooks"),
            generated_directory=os.getenv("GENERATED_DIRECTORY", ".generated"),
            posted_directory=os.getenv("POSTED_DIRECTORY", ".posted"),
            base_branch=os.getenv("BASE_BRANCH", "main"),
            min_posts_for_analysis=int(os.getenv("MIN_POSTS_FOR_ANALYSIS", "3")),
            style_profile_version=os.getenv("STYLE_PROFILE_VERSION", "1.0.0")
        )

    def validate(self) -> ValidationResult:
        """Validate configuration settings."""
        errors = []
        warnings = []

        # Check required API keys
        if not self.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY is required")

        if self.auto_post_enabled:
            if not all([
                self.twitter_api_key,
                self.twitter_api_secret,
                self.twitter_access_token,
                self.twitter_access_token_secret
            ]):
                errors.append("Twitter API credentials are required when auto_post_enabled is True")

        # Validate numeric ranges
        if self.max_tweets_per_thread < 1 or self.max_tweets_per_thread > 25:
            warnings.append("max_tweets_per_thread should be between 1 and 25")

        if self.hook_variations_count < 1 or self.hook_variations_count > 10:
            warnings.append("hook_variations_count should be between 1 and 10")

        # Determine status
        if errors:
            status = ValidationStatus.ERROR
            message = f"Configuration validation failed: {'; '.join(errors)}"
        elif warnings:
            status = ValidationStatus.WARNING
            message = f"Configuration warnings: {'; '.join(warnings)}"
        else:
            status = ValidationStatus.VALID
            message = "Configuration is valid"

        return ValidationResult(
            status=status,
            message=message,
            details={"errors": errors, "warnings": warnings}
        )