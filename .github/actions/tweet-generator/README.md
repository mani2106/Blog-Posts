# GitHub Tweet Thread Generator

A powerful GitHub Action that automatically generates engaging tweet threads from your blog posts using AI, with built-in style analysis and engagement optimization.

## Features

- 🤖 **AI-Powered Generation**: Uses OpenRouter API with multiple specialized models
- 📝 **Style Analysis**: Learns your writing style from existing blog posts
- 🚀 **Engagement Optimization**: Applies proven social media engagement techniques
- 🔍 **Content Safety**: Built-in filtering and validation
- 📋 **Human Review**: PR-based workflow for content approval
- 🐦 **Auto-Posting**: Optional automatic posting to X/Twitter
- 📊 **Comprehensive Logging**: Detailed monitoring and metrics

## Quick Start

### 1. Add the Action to Your Workflow

Add this step to your existing GitHub Pages workflow:

```yaml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    twitter_api_key: ${{ secrets.TWITTER_API_KEY }}
    twitter_api_secret: ${{ secrets.TWITTER_API_SECRET }}
    twitter_access_token: ${{ secrets.TWITTER_ACCESS_TOKEN }}
    twitter_access_token_secret: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
  if: github.ref == 'refs/heads/main'
```

### 2. Set Up Required Secrets

In your repository settings, add these secrets:

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `TWITTER_API_KEY`: Twitter API key (optional, for auto-posting)
- `TWITTER_API_SECRET`: Twitter API secret (optional)
- `TWITTER_ACCESS_TOKEN`: Twitter access token (optional)
- `TWITTER_ACCESS_TOKEN_SECRET`: Twitter access token secret (optional)

### 3. Configure Your Blog Posts

Add frontmatter to your blog posts to control tweet generation:

```yaml
---
title: "My Amazing Blog Post"
description: "A brief description of the post"
categories: [tutorial, programming]
publish: true
auto_post: false  # Set to true for automatic posting
---
```

## Installation

### Option 1: Copy Action Files

1. Create the directory structure:
```bash
mkdir -p .github/actions/tweet-generator
```

2. Copy all files from this repository to `.github/actions/tweet-generator/`

3. Add the action step to your workflow (see Quick Start above)

### Option 2: Use as Composite Action

Reference this action directly in your workflow:

```yaml
- name: Generate tweet threads
  uses: your-username/tweet-generator@v1
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for AI models | - | Yes |
| `OPENROUTER_MODEL` | Primary model for content generation | `anthropic/claude-3-haiku` | No |
| `CREATIVE_MODEL` | Model for creative content (hooks) | `anthropic/claude-3-sonnet` | No |
| `VERIFICATION_MODEL` | Model for content validation | `anthropic/claude-3-haiku` | No |
| `MAX_TWEETS_PER_THREAD` | Maximum tweets in a thread | `10` | No |
| `ENGAGEMENT_LEVEL` | Optimization level (low/medium/high) | `high` | No |
| `AUTO_POST_ENABLED` | Global auto-posting toggle | `false` | No |
| `DRY_RUN_MODE` | Test mode without API calls | `false` | No |

### Configuration File

Create `.github/tweet-generator-config.yml` for advanced configuration:

```yaml
models:
  planning: anthropic/claude-3-haiku
  creative: anthropic/claude-3-sonnet
  verification: anthropic/claude-3-haiku

engagement:
  optimization_level: high
  hook_variations: 3
  max_hashtags: 2
  include_emojis: true

output:
  auto_post_enabled: false
  dry_run_mode: false
  max_tweets_per_thread: 10

safety:
  content_filtering: true
  profanity_check: true
  claim_flagging: true

logging:
  level: INFO
  include_metrics: true
  structured_output: true
```

## How It Works

### 1. Content Detection
- Scans for changed blog posts in `_posts` and `_notebooks` directories
- Extracts frontmatter metadata (title, categories, publish flag)
- Filters posts based on `publish: true` flag

### 2. Style Analysis
- Analyzes existing blog posts to learn your writing style
- Identifies vocabulary patterns, tone, and content structure
- Saves style profile to `.generated/writing-style-profile.json`

### 3. AI Generation
- Uses multiple specialized AI models for different tasks:
  - **Planning Model**: Thread structure and organization
  - **Creative Model**: Hook generation and engaging content
  - **Verification Model**: Content validation and safety checks

### 4. Engagement Optimization
- Applies proven engagement techniques:
  - Curiosity gap hooks
  - Contrarian takes and pattern interrupts
  - Strategic emoji placement
  - Power words and psychological triggers
  - Visual hierarchy and formatting

### 5. Content Validation
- Enforces 280-character limits per tweet
- Checks for inappropriate content and profanity
- Validates JSON structure and required fields
- Flags numeric claims for manual review

### 6. Output Management
- Saves thread drafts to `.generated/<slug>-thread.json`
- Creates or updates pull requests for review
- Optionally posts to X/Twitter if `auto_post: true`
- Tracks posted content in `.posted/<slug>.json`

## File Structure

After running the action, your repository will contain:

```
.generated/
├── writing-style-profile.json    # Your writing style analysis
└── my-post-thread.json          # Generated thread drafts

.posted/
└── my-post.json                 # Posted tweet metadata

.github/
├── actions/
│   └── tweet-generator/         # Action files
└── workflows/
    └── pages.yml               # Your workflow (modified)
```

## Frontmatter Options

Configure individual posts with these frontmatter fields:

```yaml
---
title: "Required: Post title"
description: "Optional: Brief description for context"
categories: ["Optional: List of categories"]
publish: true              # Required: Must be true to generate threads
auto_post: false          # Optional: Auto-post to Twitter if enabled
canonical_url: "Optional: Custom URL for attribution"
---
```

## Generated Output

### Thread JSON Structure

```json
{
  "post_slug": "my-amazing-post",
  "tweets": [
    "🧵 Thread: The secret technique that changed everything...",
    "1/7 Most developers struggle with this common problem...",
    "2/7 But here's what they don't tell you...",
    "..."
  ],
  "hook_variations": [
    "What if I told you there's a better way?",
    "🚨 This will blow your mind...",
    "The industry doesn't want you to know this..."
  ],
  "hashtags": ["#coding", "#productivity"],
  "engagement_score": 8.5,
  "metadata": {
    "model_used": "anthropic/claude-3-sonnet",
    "generated_at": "2024-01-15T10:30:00Z",
    "style_profile_version": "1.2.0"
  }
}
```

### Pull Request Format

The action creates PRs with:
- Thread preview with character counts
- Hook variations for selection
- Generation metadata and model info
- Review checklist for quality assurance

## Advanced Usage

### Custom Engagement Techniques

Override default engagement optimization:

```yaml
# In tweet-generator-config.yml
engagement:
  custom_hooks:
    - "Here's what nobody tells you about {topic}..."
    - "I wish I knew this {timeframe} ago..."
  power_words: ["secret", "proven", "instant", "breakthrough"]
  psychological_triggers: ["curiosity", "fomo", "social_proof"]
```

### Multi-Model Strategy

Use different models for different content types:

```yaml
models:
  technical_content: "anthropic/claude-3-sonnet"
  personal_content: "anthropic/claude-3-haiku"
  tutorial_content: "openai/gpt-4-turbo"
```

### Batch Processing

Process multiple posts efficiently:

```bash
# Set environment variable for batch mode
export BATCH_MODE=true
export MAX_CONCURRENT_POSTS=3
```

## Monitoring and Metrics

### GitHub Actions Outputs

The action provides these outputs for monitoring:

```yaml
outputs:
  threads_generated:
    description: "Number of threads generated"
  posts_processed:
    description: "Number of posts processed"
  pr_created:
    description: "PR URL if created"
  auto_posts_count:
    description: "Number of auto-posted threads"
  errors_count:
    description: "Number of errors encountered"
```

### Logging Levels

Configure logging detail:

```yaml
# Environment variable
LOGGING_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# In config file
logging:
  level: INFO
  include_api_metrics: true
  include_performance_data: true
```

### Metrics Collection

The action tracks:
- API response times and token usage
- Content generation success rates
- Engagement optimization effectiveness
- Error rates by category
- Performance metrics (memory, execution time)

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed troubleshooting guide.

### Common Issues

**Issue**: "No OpenRouter API key found"
**Solution**: Add `OPENROUTER_API_KEY` to repository secrets

**Issue**: "No posts found to process"
**Solution**: Ensure posts have `publish: true` in frontmatter

**Issue**: "Style analysis failed"
**Solution**: Ensure you have at least 3 published posts for analysis

**Issue**: "Twitter API authentication failed"
**Solution**: Verify all Twitter API credentials in secrets

## API Documentation

See [API.md](./API.md) for detailed API documentation of all components.

## Examples

See [examples/](./examples/) directory for:
- Complete workflow configurations
- Sample blog post formats
- Configuration file examples
- Custom engagement templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Support

- 📖 [Documentation](./docs/)
- 🐛 [Issue Tracker](../../issues)
- 💬 [Discussions](../../discussions)
- 📧 [Email Support](mailto:support@example.com)

---

**Made with ❤️ for the developer community**