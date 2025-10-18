# Examples

This directory contains example configurations and usage patterns for the GitHub Tweet Thread Generator.

## Directory Structure

```
examples/
├── README.md                           # This file
├── workflows/                          # GitHub workflow examples
│   ├── basic-integration.yml          # Simple integration
│   ├── advanced-workflow.yml          # Advanced configuration
│   └── multi-site-workflow.yml        # Multiple site support
├── configurations/                     # Configuration file examples
│   ├── basic-config.yml              # Basic configuration
│   ├── advanced-config.yml           # Advanced settings
│   ├── technical-blog-config.yml     # Technical content optimization
│   └── personal-blog-config.yml      # Personal content optimization
├── blog-posts/                        # Example blog post formats
│   ├── technical-tutorial.md         # Technical tutorial example
│   ├── personal-story.md             # Personal story example
│   └── product-announcement.md       # Product announcement example
└── generated-outputs/                 # Example generated content
    ├── technical-thread.json         # Technical content thread
    ├── personal-thread.json          # Personal content thread
    └── announcement-thread.json      # Announcement thread
```

## Quick Start Examples

### 1. Basic Integration

The simplest way to add tweet generation to your existing GitHub Pages workflow:

```yaml
# Add this step to your existing .github/workflows/deploy.yml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
  if: github.ref == 'refs/heads/main'
```

### 2. With Auto-Posting

Enable automatic posting to X/Twitter:

```yaml
- name: Generate and post tweet threads
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    twitter_api_key: ${{ secrets.TWITTER_API_KEY }}
    twitter_api_secret: ${{ secrets.TWITTER_API_SECRET }}
    twitter_access_token: ${{ secrets.TWITTER_ACCESS_TOKEN }}
    twitter_access_token_secret: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
    auto_post_enabled: 'true'
  if: github.ref == 'refs/heads/main'
```

### 3. Custom Configuration

Use a configuration file for advanced settings:

```yaml
- name: Generate tweet threads with custom config
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    config_file: '.github/tweet-generator-config.yml'
  if: github.ref == 'refs/heads/main'
```

## Configuration Examples

### Basic Configuration

```yaml
# .github/tweet-generator-config.yml
models:
  planning: anthropic/claude-3-haiku
  creative: anthropic/claude-3-sonnet
  verification: anthropic/claude-3-haiku

engagement:
  optimization_level: medium
  hook_variations: 2
  max_hashtags: 2

output:
  auto_post_enabled: false
  max_tweets_per_thread: 8
```

### Technical Blog Configuration

```yaml
# Optimized for technical content
models:
  planning: anthropic/claude-3-sonnet
  creative: anthropic/claude-3-sonnet
  verification: anthropic/claude-3-haiku

engagement:
  optimization_level: high
  hook_variations: 3
  max_hashtags: 2
  custom_hooks:
    - "Here's what most developers get wrong about {topic}..."
    - "I spent {timeframe} learning {topic} so you don't have to..."
    - "The {topic} technique that changed my development workflow..."
  power_words: ["breakthrough", "secret", "proven", "advanced", "expert"]

content:
  technical_terminology_boost: true
  code_snippet_optimization: true
  tutorial_structure_preference: true

output:
  auto_post_enabled: false
  max_tweets_per_thread: 12
  include_code_previews: true
```

### Personal Blog Configuration

```yaml
# Optimized for personal content and storytelling
models:
  planning: anthropic/claude-3-haiku
  creative: anthropic/claude-3-sonnet
  verification: anthropic/claude-3-haiku

engagement:
  optimization_level: high
  hook_variations: 4
  max_hashtags: 1
  custom_hooks:
    - "Last {timeframe}, something happened that changed everything..."
    - "I used to think {belief}, but then I discovered..."
    - "Here's the story nobody talks about..."
  psychological_triggers: ["relatability", "vulnerability", "inspiration"]

content:
  story_structure_preference: true
  personal_anecdote_boost: true
  emotional_language_enhancement: true

output:
  auto_post_enabled: true
  max_tweets_per_thread: 10
  include_personal_cta: true
```

## Blog Post Examples

### Technical Tutorial Format

```markdown
---
title: "Building a REST API with FastAPI and PostgreSQL"
description: "Complete guide to building production-ready APIs"
categories: [tutorial, python, api, database]
publish: true
auto_post: false
canonical_url: "https://yourblog.com/fastapi-postgresql-tutorial"
---

# Building a REST API with FastAPI and PostgreSQL

In this comprehensive tutorial, we'll build a production-ready REST API using FastAPI and PostgreSQL. You'll learn best practices for database design, API architecture, and deployment.

## What You'll Learn

- Setting up FastAPI with async/await
- Database modeling with SQLAlchemy
- Authentication and authorization
- API testing and documentation
- Deployment strategies

## Prerequisites

Before we start, make sure you have:
- Python 3.8+
- PostgreSQL installed
- Basic knowledge of REST APIs

[Rest of tutorial content...]
```

**Generated Thread Example:**
```
🧵 Thread: The FastAPI + PostgreSQL combo that's changing how developers build APIs

1/10 Most developers struggle with building production-ready APIs that scale. Here's the stack that solved it for me...

2/10 FastAPI isn't just another Python framework. It's async-first, automatically generates docs, and has built-in validation that catches bugs before they hit production.

[Continue thread...]
```

### Personal Story Format

```markdown
---
title: "How I Overcame Impostor Syndrome as a Self-Taught Developer"
description: "My journey from self-doubt to confidence in tech"
categories: [personal, career, mental-health]
publish: true
auto_post: true
canonical_url: "https://yourblog.com/overcoming-impostor-syndrome"
---

# How I Overcame Impostor Syndrome as a Self-Taught Developer

Three years ago, I was convinced I didn't belong in tech. Despite landing my first developer job, I felt like a fraud waiting to be exposed. Here's how I transformed that self-doubt into confidence.

## The Breaking Point

It was during my first code review when my senior developer pointed out several issues with my pull request. Instead of seeing it as learning opportunity, I spiraled into self-doubt...

[Rest of personal story...]
```

**Generated Thread Example:**
```
🧵 Thread: The impostor syndrome story that changed my entire tech career

1/8 Three years ago, I was convinced I didn't belong in tech. Despite having a developer job, I felt like a fraud waiting to be exposed.

2/8 It all came to a head during my first code review. My senior dev found issues with my PR, and instead of learning, I spiraled into self-doubt...

[Continue thread...]
```

## Workflow Integration Examples

### Complete Jekyll Workflow

```yaml
# .github/workflows/pages.yml
name: Build and Deploy Jekyll Site

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write
  pull-requests: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Needed for git diff

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true

      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v3

      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production

      - name: Generate tweet threads
        uses: ./.github/actions/tweet-generator
        with:
          openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
          twitter_api_key: ${{ secrets.TWITTER_API_KEY }}
          twitter_api_secret: ${{ secrets.TWITTER_API_SECRET }}
          twitter_access_token: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          twitter_access_token_secret: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
          config_file: '.github/tweet-generator-config.yml'
        if: github.ref == 'refs/heads/main'

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

### Multi-Site Workflow

```yaml
# .github/workflows/multi-site.yml
name: Multi-Site Tweet Generation

on:
  push:
    branches: [ main ]

jobs:
  generate-tweets:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        site:
          - name: "tech-blog"
            posts_dir: "_posts/tech"
            config: ".github/configs/tech-config.yml"
          - name: "personal-blog"
            posts_dir: "_posts/personal"
            config: ".github/configs/personal-config.yml"

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate tweets for ${{ matrix.site.name }}
        uses: ./.github/actions/tweet-generator
        with:
          openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
          posts_directory: ${{ matrix.site.posts_dir }}
          config_file: ${{ matrix.site.config }}
          output_prefix: ${{ matrix.site.name }}
```

## Environment Variable Examples

### Development Environment

```bash
# .env.development
OPENROUTER_API_KEY=sk-or-your-dev-key
OPENROUTER_MODEL=anthropic/claude-3-haiku
ENGAGEMENT_LEVEL=medium
MAX_TWEETS_PER_THREAD=8
AUTO_POST_ENABLED=false
DRY_RUN_MODE=true
LOGGING_LEVEL=DEBUG
```

### Production Environment

```bash
# Set in GitHub Secrets
OPENROUTER_API_KEY=sk-or-your-production-key
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret

# Set in workflow
OPENROUTER_MODEL=anthropic/claude-3-sonnet
ENGAGEMENT_LEVEL=high
MAX_TWEETS_PER_THREAD=10
AUTO_POST_ENABLED=true
DRY_RUN_MODE=false
LOGGING_LEVEL=INFO
```

## Testing Examples

### Local Testing Script

```bash
#!/bin/bash
# test-local.sh

# Set up test environment
export OPENROUTER_API_KEY="your-test-key"
export DRY_RUN_MODE="true"
export LOGGING_LEVEL="DEBUG"

# Create test post
cat > _posts/$(date +%Y-%m-%d)-test-post.md << EOF
---
title: "Test Post for Tweet Generation"
description: "Testing the tweet generator"
categories: [test]
publish: true
auto_post: false
---

# Test Post

This is a test post to verify the tweet generator works correctly.

## Key Points

- Point one
- Point two
- Point three

## Conclusion

This concludes our test post.
EOF

# Run the generator
python .github/actions/tweet-generator/generate_and_commit.py

# Check output
echo "Generated files:"
ls -la .generated/
ls -la .posted/

# Clean up
rm _posts/$(date +%Y-%m-%d)-test-post.md
```

### GitHub Actions Test Workflow

```yaml
# .github/workflows/test-tweet-generator.yml
name: Test Tweet Generator

on:
  pull_request:
    paths:
      - '.github/actions/tweet-generator/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create test post
        run: |
          mkdir -p _posts
          cat > _posts/$(date +%Y-%m-%d)-test-post.md << EOF
          ---
          title: "Test Post"
          publish: true
          auto_post: false
          ---
          # Test content
          This is test content for validation.
          EOF

      - name: Test tweet generation (dry run)
        uses: ./.github/actions/tweet-generator
        with:
          openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
          dry_run_mode: 'true'

      - name: Validate output
        run: |
          if [ ! -f .generated/test-post-thread.json ]; then
            echo "Error: Thread file not generated"
            exit 1
          fi

          if ! python -m json.tool .generated/test-post-thread.json > /dev/null; then
            echo "Error: Invalid JSON output"
            exit 1
          fi

          echo "✅ Test passed: Valid thread generated"
```

## Customization Examples

### Custom Hook Templates

```yaml
# Custom engagement hooks for different content types
engagement:
  custom_hooks:
    tutorial:
      - "The {topic} tutorial that will save you hours of debugging..."
      - "I wish someone taught me {topic} this way when I started..."
      - "Here's the {topic} approach that finally made it click..."

    personal:
      - "Last {timeframe}, I learned something that changed my perspective on {topic}..."
      - "The {topic} mistake that taught me more than any success..."
      - "Here's what {timeframe} of {topic} taught me about {lesson}..."

    announcement:
      - "🚀 After {timeframe} of work, I'm excited to share {product}..."
      - "The {product} launch story: from idea to reality..."
      - "Why I built {product} and what it means for {audience}..."
```

### Custom Engagement Metrics

```python
# Custom engagement scoring
def calculate_custom_engagement_score(tweets: List[str]) -> float:
    """Calculate engagement score with custom weights."""

    score = 0.0

    for i, tweet in enumerate(tweets):
        # Hook quality (first tweet)
        if i == 0:
            if any(hook in tweet.lower() for hook in ["what if", "here's why", "the secret"]):
                score += 2.0

        # Thread continuity
        if f"{i+1}/" in tweet:
            score += 1.0

        # Engagement elements
        if "?" in tweet:
            score += 0.5
        if any(emoji in tweet for emoji in ["🧵", "🚀", "💡", "🔥"]):
            score += 0.3

        # Call to action (last tweet)
        if i == len(tweets) - 1:
            if any(cta in tweet.lower() for cta in ["what do you think", "share your", "tag someone"]):
                score += 1.5

    return min(score, 10.0)  # Cap at 10
```

## Migration Examples

### From Manual Posting

If you're currently posting manually, here's how to migrate:

1. **Audit existing content**:
```bash
# Check your existing posts
find _posts -name "*.md" | head -10 | xargs grep -l "title:"
```

2. **Add frontmatter gradually**:
```yaml
# Start with basic frontmatter
---
title: "Your Post Title"
publish: true
auto_post: false  # Start with manual review
---
```

3. **Test with dry run**:
```yaml
# Test without posting
- name: Test tweet generation
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    dry_run_mode: 'true'
```

4. **Gradually enable auto-posting**:
```yaml
# Enable for specific posts
---
title: "Well-tested post"
publish: true
auto_post: true  # Enable after testing
---
```

### From Other Platforms

Migrating from other blog platforms:

```python
# Convert WordPress exports
def convert_wordpress_post(wp_post):
    """Convert WordPress post to Jekyll format."""

    frontmatter = {
        'title': wp_post['title'],
        'date': wp_post['date'],
        'categories': wp_post['categories'],
        'publish': True,
        'auto_post': False
    }

    content = f"---\n{yaml.dump(frontmatter)}---\n\n{wp_post['content']}"

    filename = f"_posts/{wp_post['date']}-{slugify(wp_post['title'])}.md"

    with open(filename, 'w') as f:
        f.write(content)
```

## Performance Optimization Examples

### Caching Configuration

```yaml
# Enable caching for better performance
performance:
  enable_style_profile_cache: true
  cache_duration_hours: 24
  enable_api_response_cache: true
  max_concurrent_requests: 3

  # Optimize for large repositories
  incremental_analysis: true
  max_posts_per_analysis: 50
  skip_old_posts_days: 365
```

### Batch Processing

```yaml
# Process multiple posts efficiently
batch:
  enabled: true
  max_posts_per_batch: 5
  delay_between_batches_seconds: 10

  # Prioritize recent posts
  sort_by_date: true
  process_recent_first: true
```

---

These examples provide comprehensive coverage of different use cases and configurations. Choose the examples that best match your blog type and requirements, then customize as needed.