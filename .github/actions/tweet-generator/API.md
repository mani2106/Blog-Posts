# API Documentation

This document provides detailed API documentation for all components and interfaces in the GitHub Tweet Thread Generator.

## Table of Contents

- [Core Data Models](#core-data-models)
- [Content Detection](#content-detection)
- [Style Analysis](#style-analysis)
- [AI Orchestration](#ai-orchestration)
- [Engagement Optimization](#engagement-optimization)
- [Content Validation](#content-validation)
- [Output Management](#output-management)
- [Configuration](#configuration)
- [Error Handling](#error-handling)

## Core Data Models

### BlogPost

Represents a blog post with metadata and content.

```python
@dataclass
class BlogPost:
    """Represents a blog post with metadata and content."""

    file_path: str                    # Path to the blog post file
    title: str                        # Post title from frontmatter
    content: str                      # Full post content (markdown/text)
    frontmatter: Dict[str, Any]       # Parsed frontmatter metadata
    canonical_url: str                # URL for attribution
    categories: List[str]             # Post categories
    summary: Optional[str] = None     # Brief post summary
    auto_post: bool = False           # Auto-posting flag

    @classmethod
    def from_file(cls, file_path: str) -> 'BlogPost':
        """Create BlogPost instance from file."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""

    def get_slug(self) -> str:
        """Generate URL-friendly slug from title."""
```

### StyleProfile

Contains analyzed writing style patterns and preferences.

```python
@dataclass
class StyleProfile:
    """Contains analyzed writing style patterns and preferences."""

    vocabulary_patterns: VocabularyProfile    # Common words and phrases
    tone_indicators: ToneProfile              # Tone and sentiment patterns
    content_structures: StructureProfile      # Content organization patterns
    emoji_usage: EmojiProfile                 # Emoji usage patterns
    technical_terminology: List[str]          # Technical terms used
    created_at: datetime                      # Profile creation timestamp
    version: str                              # Profile version

    @classmethod
    def from_posts(cls, posts: List[BlogPost]) -> 'StyleProfile':
        """Build style profile from blog posts."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""

    def save(self, file_path: str) -> None:
        """Save profile to JSON file."""

    @classmethod
    def load(cls, file_path: str) -> 'StyleProfile':
        """Load profile from JSON file."""
```

### ThreadData

Represents a generated tweet thread with metadata.

```python
@dataclass
class ThreadData:
    """Represents a generated tweet thread with metadata."""

    post_slug: str                    # Source post identifier
    tweets: List[str]                 # Individual tweet content
    hook_variations: List[str]        # Alternative opening hooks
    hashtags: List[str]               # Recommended hashtags
    engagement_score: float           # Calculated engagement score
    model_used: str                   # AI model used for generation
    prompt_version: str               # Prompt template version
    generated_at: datetime            # Generation timestamp
    style_profile_version: str        # Style profile version used

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""

    def save(self, file_path: str) -> None:
        """Save thread data to JSON file."""

    @classmethod
    def load(cls, file_path: str) -> 'ThreadData':
        """Load thread data from JSON file."""

    def get_character_counts(self) -> List[int]:
        """Get character count for each tweet."""

    def validate_limits(self) -> ValidationResult:
        """Validate tweet character limits."""
```

## Content Detection

### ContentDetector

Detects changed blog posts and extracts metadata.

```python
class ContentDetector:
    """Detects changed blog posts and extracts metadata."""

    def __init__(self, posts_dir: str = "_posts", notebooks_dir: str = "_notebooks"):
        """Initialize content detector with directory paths."""

    def detect_changed_posts(self, base_branch: str = "main") -> List[BlogPost]:
        """
        Detect blog posts that have changed since the base branch.

        Args:
            base_branch: Git branch to compare against

        Returns:
            List of BlogPost objects for changed posts

        Raises:
            GitError: If git operations fail
            FileNotFoundError: If post directories don't exist
        """

    def extract_frontmatter(self, file_path: str) -> Dict[str, Any]:
        """
        Extract and parse frontmatter from a blog post file.

        Args:
            file_path: Path to the blog post file

        Returns:
            Dictionary containing frontmatter data

        Raises:
            FrontmatterError: If frontmatter parsing fails
            FileNotFoundError: If file doesn't exist
        """

    def should_process_post(self, post: BlogPost) -> bool:
        """
        Determine if a post should be processed for tweet generation.

        Args:
            post: BlogPost object to evaluate

        Returns:
            True if post should be processed, False otherwise
        """

    def get_all_posts(self) -> List[BlogPost]:
        """
        Get all blog posts from configured directories.

        Returns:
            List of all BlogPost objects
        """
```

## Style Analysis

### StyleAnalyzer

Analyzes writing style from existing blog posts.

```python
class StyleAnalyzer:
    """Analyzes writing style from existing blog posts."""

    def __init__(self):
        """Initialize style analyzer with NLP tools."""

    def build_style_profile(self, posts_dir: str, notebooks_dir: str) -> StyleProfile:
        """
        Build comprehensive style profile from blog posts.

        Args:
            posts_dir: Directory containing markdown posts
            notebooks_dir: Directory containing Jupyter notebooks

        Returns:
            StyleProfile object with analyzed patterns

        Raises:
            InsufficientContentError: If not enough content for analysis
            AnalysisError: If style analysis fails
        """

    def analyze_vocabulary_patterns(self, content: List[str]) -> VocabularyProfile:
        """
        Analyze vocabulary usage patterns.

        Args:
            content: List of text content to analyze

        Returns:
            VocabularyProfile with word frequency and patterns
        """

    def extract_tone_indicators(self, content: List[str]) -> ToneProfile:
        """
        Extract tone and sentiment indicators.

        Args:
            content: List of text content to analyze

        Returns:
            ToneProfile with tone characteristics
        """

    def identify_content_structures(self, posts: List[BlogPost]) -> StructureProfile:
        """
        Identify preferred content organization patterns.

        Args:
            posts: List of BlogPost objects to analyze

        Returns:
            StructureProfile with structural preferences
        """

    def analyze_emoji_usage(self, content: List[str]) -> EmojiProfile:
        """
        Analyze emoji usage patterns and preferences.

        Args:
            content: List of text content to analyze

        Returns:
            EmojiProfile with emoji usage patterns
        """
```

## AI Orchestration

### AIOrchestrator

Manages AI model interactions and content generation.

```python
class AIOrchestrator:
    """Manages AI model interactions and content generation."""

    def __init__(self, config: GeneratorConfig):
        """
        Initialize AI orchestrator with configuration.

        Args:
            config: Generator configuration object
        """

    async def generate_thread_plan(self, post: BlogPost, style_profile: StyleProfile) -> ThreadPlan:
        """
        Generate thread structure and organization plan.

        Args:
            post: BlogPost to create thread for
            style_profile: Author's writing style profile

        Returns:
            ThreadPlan with structure and key points

        Raises:
            APIError: If OpenRouter API call fails
            ValidationError: If response format is invalid
        """

    async def generate_hook_variations(self, post: BlogPost, count: int = 3) -> List[str]:
        """
        Generate multiple hook variations for thread opening.

        Args:
            post: BlogPost to create hooks for
            count: Number of hook variations to generate

        Returns:
            List of hook strings
        """

    async def generate_thread_content(self, plan: ThreadPlan, style_profile: StyleProfile) -> List[str]:
        """
        Generate full thread content based on plan.

        Args:
            plan: ThreadPlan with structure and key points
            style_profile: Author's writing style profile

        Returns:
            List of tweet strings
        """

    async def verify_content_quality(self, tweets: List[str]) -> ValidationResult:
        """
        Verify generated content quality and safety.

        Args:
            tweets: List of tweet strings to verify

        Returns:
            ValidationResult with quality assessment
        """

    def _build_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Build AI prompt from template and context."""

    async def _call_openrouter(self, prompt: str, model: str) -> Dict[str, Any]:
        """Make API call to OpenRouter with retry logic."""
```

## Engagement Optimization

### EngagementOptimizer

Applies proven engagement techniques to content.

```python
class EngagementOptimizer:
    """Applies proven engagement techniques to content."""

    def __init__(self, config: EngagementConfig):
        """Initialize with engagement configuration."""

    def optimize_hooks(self, content: str, hook_types: List[str]) -> List[str]:
        """
        Generate optimized hooks using specified techniques.

        Args:
            content: Source content for hook generation
            hook_types: List of hook types to generate

        Returns:
            List of optimized hook strings

        Available hook types:
            - "curiosity_gap": "What if I told you..."
            - "contrarian": "Everyone says X, but..."
            - "statistic": "X% of people don't know..."
            - "story": "Last week something happened..."
            - "value_proposition": "Here's how to X in Y minutes..."
        """

    def apply_thread_structure(self, tweets: List[str]) -> List[str]:
        """
        Apply thread arc structure for maximum engagement.

        Args:
            tweets: Raw tweet content

        Returns:
            Structured tweets with engagement elements
        """

    def add_engagement_elements(self, tweet: str, position: int, total: int) -> str:
        """
        Add engagement elements to individual tweets.

        Args:
            tweet: Tweet content
            position: Position in thread (0-based)
            total: Total tweets in thread

        Returns:
            Tweet with engagement elements added
        """

    def optimize_hashtags(self, content: str, categories: List[str]) -> List[str]:
        """
        Select optimal hashtags for content and audience.

        Args:
            content: Tweet thread content
            categories: Post categories

        Returns:
            List of 1-2 optimal hashtags
        """

    def apply_visual_formatting(self, tweet: str) -> str:
        """
        Apply visual hierarchy and formatting techniques.

        Args:
            tweet: Raw tweet content

        Returns:
            Formatted tweet with visual enhancements
        """

    def calculate_engagement_score(self, tweets: List[str]) -> float:
        """
        Calculate predicted engagement score for thread.

        Args:
            tweets: List of tweet strings

        Returns:
            Engagement score (0-10 scale)
        """
```

## Content Validation

### ContentValidator

Validates content quality, safety, and platform compliance.

```python
class ContentValidator:
    """Validates content quality, safety, and platform compliance."""

    def __init__(self, config: ValidationConfig):
        """Initialize with validation configuration."""

    def validate_character_limits(self, tweets: List[str]) -> ValidationResult:
        """
        Validate tweet character limits (280 chars including URLs).

        Args:
            tweets: List of tweet strings to validate

        Returns:
            ValidationResult with limit compliance status
        """

    def check_content_safety(self, content: str) -> SafetyResult:
        """
        Check content for safety and appropriateness.

        Args:
            content: Text content to check

        Returns:
            SafetyResult with safety assessment

        Checks performed:
            - Profanity detection
            - Hate speech detection
            - Spam indicators
            - Inappropriate content patterns
        """

    def verify_json_structure(self, data: Dict[str, Any]) -> bool:
        """
        Verify JSON response structure from AI models.

        Args:
            data: Dictionary to validate

        Returns:
            True if structure is valid, False otherwise
        """

    def validate_engagement_elements(self, tweets: List[str]) -> ValidationResult:
        """
        Validate proper engagement element placement.

        Args:
            tweets: List of tweet strings

        Returns:
            ValidationResult with engagement validation status
        """

    def flag_numeric_claims(self, content: str) -> List[NumericClaim]:
        """
        Flag numeric claims for manual review.

        Args:
            content: Text content to analyze

        Returns:
            List of NumericClaim objects found
        """
```

## Output Management

### OutputManager

Handles file operations, PR creation, and auto-posting.

```python
class OutputManager:
    """Handles file operations, PR creation, and auto-posting."""

    def __init__(self, config: OutputConfig):
        """Initialize with output configuration."""

    def save_thread_draft(self, thread: ThreadData, output_path: str) -> None:
        """
        Save thread draft to JSON file.

        Args:
            thread: ThreadData object to save
            output_path: File path for output

        Raises:
            FileWriteError: If file write operation fails
        """

    async def create_or_update_pr(self, thread: ThreadData, post: BlogPost) -> str:
        """
        Create or update pull request for thread review.

        Args:
            thread: ThreadData object
            post: Source BlogPost object

        Returns:
            PR URL string

        Raises:
            GitHubAPIError: If PR creation fails
        """

    async def post_to_twitter(self, thread: ThreadData) -> PostResult:
        """
        Post thread to X/Twitter platform.

        Args:
            thread: ThreadData to post

        Returns:
            PostResult with tweet IDs and metadata

        Raises:
            TwitterAPIError: If posting fails
            RateLimitError: If rate limit exceeded
        """

    def save_posted_metadata(self, result: PostResult, output_path: str) -> None:
        """
        Save posted tweet metadata for duplicate prevention.

        Args:
            result: PostResult from Twitter posting
            output_path: File path for metadata storage
        """

    def check_already_posted(self, post_slug: str) -> bool:
        """
        Check if post has already been posted to Twitter.

        Args:
            post_slug: Post identifier

        Returns:
            True if already posted, False otherwise
        """
```

## Configuration

### GeneratorConfig

Main configuration object for the tweet generator.

```python
@dataclass
class GeneratorConfig:
    """Main configuration for tweet generator."""

    # AI Model Configuration
    openrouter_model: str = "anthropic/claude-3-haiku"
    creative_model: str = "anthropic/claude-3-sonnet"
    verification_model: str = "anthropic/claude-3-haiku"

    # Content Configuration
    max_tweets_per_thread: int = 10
    hook_variations_count: int = 3
    max_hashtags: int = 2

    # Engagement Configuration
    engagement_optimization_level: str = "high"  # low, medium, high
    include_emojis: bool = True
    use_power_words: bool = True

    # Output Configuration
    auto_post_enabled: bool = False
    dry_run_mode: bool = False
    create_prs: bool = True

    # API Configuration
    api_timeout: int = 60
    max_retries: int = 3
    retry_delay: int = 5

    # Logging Configuration
    logging_level: str = "INFO"
    include_metrics: bool = True
    structured_output: bool = True

    @classmethod
    def from_env(cls) -> 'GeneratorConfig':
        """Create configuration from environment variables."""

    @classmethod
    def from_file(cls, file_path: str) -> 'GeneratorConfig':
        """Load configuration from YAML file."""

    def validate(self) -> ValidationResult:
        """Validate configuration values."""
```

## Error Handling

### Custom Exceptions

```python
class TweetGeneratorError(Exception):
    """Base exception for tweet generator errors."""
    pass

class APIError(TweetGeneratorError):
    """Raised when API calls fail."""

    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ValidationError(TweetGeneratorError):
    """Raised when content validation fails."""

    def __init__(self, message: str, validation_type: str, content: str = None):
        super().__init__(message)
        self.validation_type = validation_type
        self.content = content

class ContentError(TweetGeneratorError):
    """Raised when content processing fails."""
    pass

class ConfigurationError(TweetGeneratorError):
    """Raised when configuration is invalid."""
    pass

class GitHubAPIError(APIError):
    """Raised when GitHub API operations fail."""
    pass

class TwitterAPIError(APIError):
    """Raised when Twitter API operations fail."""
    pass

class OpenRouterAPIError(APIError):
    """Raised when OpenRouter API operations fail."""
    pass
```

### Error Response Format

```python
@dataclass
class ErrorResponse:
    """Standardized error response format."""

    error_code: str           # Unique error identifier
    message: str              # Human-readable error message
    details: Dict[str, Any]   # Additional error context
    timestamp: datetime       # When error occurred
    component: str            # Component that generated error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
```

## Usage Examples

### Basic Usage

```python
from src.content_detector import ContentDetector
from src.style_analyzer import StyleAnalyzer
from src.ai_orchestrator import AIOrchestrator
from src.engagement_optimizer import EngagementOptimizer
from src.output_manager import OutputManager

# Initialize components
detector = ContentDetector()
analyzer = StyleAnalyzer()
orchestrator = AIOrchestrator(config)
optimizer = EngagementOptimizer(config.engagement)
output_manager = OutputManager(config.output)

# Process blog posts
posts = detector.detect_changed_posts()
style_profile = analyzer.build_style_profile("_posts", "_notebooks")

for post in posts:
    # Generate thread
    plan = await orchestrator.generate_thread_plan(post, style_profile)
    tweets = await orchestrator.generate_thread_content(plan, style_profile)

    # Optimize for engagement
    optimized_tweets = optimizer.apply_thread_structure(tweets)
    hooks = optimizer.optimize_hooks(post.content, ["curiosity_gap", "value_proposition"])

    # Create thread data
    thread = ThreadData(
        post_slug=post.get_slug(),
        tweets=optimized_tweets,
        hook_variations=hooks,
        hashtags=optimizer.optimize_hashtags(post.content, post.categories),
        engagement_score=optimizer.calculate_engagement_score(optimized_tweets),
        model_used=config.openrouter_model,
        prompt_version="1.0",
        generated_at=datetime.now(),
        style_profile_version=style_profile.version
    )

    # Save and create PR
    output_manager.save_thread_draft(thread, f".generated/{post.get_slug()}-thread.json")
    pr_url = await output_manager.create_or_update_pr(thread, post)

    # Auto-post if enabled
    if post.auto_post and config.auto_post_enabled:
        result = await output_manager.post_to_twitter(thread)
        output_manager.save_posted_metadata(result, f".posted/{post.get_slug()}.json")
```

### Custom Hook Generation

```python
# Generate custom hooks
optimizer = EngagementOptimizer(config.engagement)

hooks = optimizer.optimize_hooks(
    content="Learn advanced Python techniques",
    hook_types=["curiosity_gap", "contrarian", "value_proposition"]
)

# Output:
# [
#     "What if I told you most Python developers are missing these advanced techniques?",
#     "Everyone learns Python basics, but here's what they don't teach you...",
#     "Master these 5 Python techniques in 10 minutes and level up your code"
# ]
```

### Style Profile Analysis

```python
# Analyze writing style
analyzer = StyleAnalyzer()
profile = analyzer.build_style_profile("_posts", "_notebooks")

print(f"Vocabulary patterns: {len(profile.vocabulary_patterns.common_words)}")
print(f"Tone: {profile.tone_indicators.primary_tone}")
print(f"Technical terms: {profile.technical_terminology[:10]}")
print(f"Emoji usage: {profile.emoji_usage.frequency}")
```

---

This API documentation provides comprehensive coverage of all components and interfaces in the GitHub Tweet Thread Generator. For implementation examples and usage patterns, see the main README and example configurations.