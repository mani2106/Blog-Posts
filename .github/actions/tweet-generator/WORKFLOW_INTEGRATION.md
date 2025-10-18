# GitHub Pages Workflow Integration Guide

This guide shows how to integrate the Tweet Thread Generator with existing GitHub Pages workflows.

## Quick Start

### 1. Basic Jekyll Integration

Add this step to your existing `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for git diff analysis

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true

      - name: Build Jekyll site
        run: bundle exec jekyll build

      # Add tweet generation step
      - name: Generate tweet threads
        uses: ./.github/actions/tweet-generator
        with:
          openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
          twitter_api_key: ${{ secrets.TWITTER_API_KEY }}
          twitter_api_secret: ${{ secrets.TWITTER_API_SECRET }}
          twitter_access_token: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          twitter_access_token_secret: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
        if: github.ref == 'refs/heads/main'

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_site
```

### 2. Fastpages Integration

For fastpages repositories, modify your existing workflow:

```yaml
name: CI
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  build-site:
    runs-on: ubuntu-latest
    steps:
      - name: Copy Repository Contents
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: convert notebooks and word docs to posts
        uses: ./_action_files
        with:
          BOOL_SAVE_MARKDOWN: true

      # Add tweet generation after content conversion
      - name: Generate tweet threads
        uses: ./.github/actions/tweet-generator
        with:
          openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
          posts_directory: "_posts"
          notebooks_directory: "_notebooks"
          dry_run: ${{ github.event_name == 'pull_request' }}
        if: github.ref == 'refs/heads/master' || github.event_name == 'pull_request'

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        if: github.event_name == 'push'
        with:
          deploy_key: ${{ secrets.SSH_DEPLOY_KEY }}
          publish_dir: ./_site
```

## Configuration Options

### Environment Variables

Set these in your repository secrets:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for AI generation |
| `TWITTER_API_KEY` | No* | Twitter API key for auto-posting |
| `TWITTER_API_SECRET` | No* | Twitter API secret |
| `TWITTER_ACCESS_TOKEN` | No* | Twitter access token |
| `TWITTER_ACCESS_TOKEN_SECRET` | No* | Twitter access token secret |

*Required only if auto-posting is enabled

### Action Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `openrouter_api_key` | Yes | - | OpenRouter API key |
| `twitter_api_key` | No | - | Twitter API key |
| `posts_directory` | No | `_posts` | Directory containing blog posts |
| `notebooks_directory` | No | `_notebooks` | Directory containing notebooks |
| `dry_run` | No | `false` | Run without creating PRs or posting |
| `engagement_level` | No | `high` | Engagement optimization level |
| `max_tweets_per_thread` | No | `10` | Maximum tweets per thread |

### YAML Configuration

Create `.github/tweet-generator-config.yml`:

```yaml
models:
  planning: anthropic/claude-3-haiku
  creative: anthropic/claude-3-sonnet
  verification: anthropic/claude-3-haiku

engagement:
  optimization_level: high
  hook_variations: 3
  max_hashtags: 2

output:
  auto_post_enabled: false
  dry_run_mode: false
  max_tweets_per_thread: 10

directories:
  posts: "_posts"
  notebooks: "_notebooks"
  generated: ".generated"
  posted: ".posted"
```

## Advanced Workflows

### 1. Conditional Auto-Posting

Only auto-post on production deployments:

```yaml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    twitter_api_key: ${{ secrets.TWITTER_API_KEY }}
    auto_post_enabled: ${{ github.ref == 'refs/heads/main' && !github.event.pull_request }}
  env:
    AUTO_POST_ENABLED: ${{ github.ref == 'refs/heads/main' }}
```

### 2. Multi-Environment Setup

Different configurations for staging and production:

```yaml
- name: Generate tweet threads (Staging)
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    dry_run: true
    engagement_level: medium
  if: github.event_name == 'pull_request'

- name: Generate tweet threads (Production)
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    twitter_api_key: ${{ secrets.TWITTER_API_KEY }}
    engagement_level: high
    auto_post_enabled: true
  if: github.ref == 'refs/heads/main'
```

### 3. Scheduled Content Generation

Generate threads for older posts on a schedule:

```yaml
name: Weekly Thread Generation
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC

jobs:
  generate-threads:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate threads for recent posts
        uses: ./.github/actions/tweet-generator
        with:
          openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
          process_all_posts: true
          max_posts_to_process: 5
        env:
          PROCESS_RECENT_POSTS: "7"  # Process posts from last 7 days
```

## Troubleshooting

### Common Issues

#### 1. "No changed posts found"

**Cause**: Git diff analysis isn't finding modified posts.

**Solutions**:
- Ensure `fetch-depth: 0` in checkout action
- Check that posts have `publish: true` in frontmatter
- Verify posts are in the correct directory (`_posts` or `_notebooks`)

#### 2. "OpenRouter API authentication failed"

**Cause**: Invalid or missing API key.

**Solutions**:
- Verify `OPENROUTER_API_KEY` is set in repository secrets
- Check API key is valid and has sufficient credits
- Ensure secret name matches exactly in workflow

#### 3. "Style analysis failed"

**Cause**: Insufficient content for analysis or parsing errors.

**Solutions**:
- Ensure at least 3 published posts exist
- Check posts have valid frontmatter
- Review error logs for specific parsing issues

#### 4. "Thread validation failed"

**Cause**: Generated content doesn't meet platform requirements.

**Solutions**:
- Check character limits (280 chars per tweet)
- Review content for safety violations
- Adjust engagement optimization level

### Debug Mode

Enable detailed logging:

```yaml
- name: Generate tweet threads (Debug)
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    dry_run: true
  env:
    DEBUG: "true"
    LOG_LEVEL: "DEBUG"
```

### Manual Testing

Test locally before deployment:

```bash
# Set environment variables
export OPENROUTER_API_KEY="your-key-here"
export DRY_RUN="true"

# Run the generator
cd .github/actions/tweet-generator
python generate_and_commit.py
```

## Migration Guide

### From Manual Posting

1. **Backup existing content**: Save current social media posts
2. **Set up secrets**: Add required API keys to repository secrets
3. **Test with dry run**: Enable `dry_run: true` initially
4. **Gradual rollout**: Start with PR-only mode, then enable auto-posting

### From Other Tools

1. **Export style data**: If using other tools, export writing style preferences
2. **Update frontmatter**: Ensure posts have required metadata
3. **Configure directories**: Update paths if using non-standard directories
4. **Test integration**: Run with existing workflow to verify compatibility

## Best Practices

### 1. Content Strategy

- Use descriptive post titles for better thread hooks
- Include relevant categories for hashtag optimization
- Write engaging summaries in frontmatter
- Use `auto_post: true` selectively for high-confidence content

### 2. Security

- Never commit API keys to repository
- Use repository secrets for all credentials
- Regularly rotate API keys
- Monitor API usage and costs

### 3. Quality Control

- Always review generated threads before auto-posting
- Use PR workflow for editorial oversight
- Monitor engagement metrics to refine style
- Adjust optimization levels based on performance

### 4. Workflow Optimization

- Run on main branch only for production
- Use dry run mode for pull requests
- Set appropriate timeouts for API calls
- Cache dependencies to improve build times

## Support

For additional help:

1. Check the [main README](README.md) for detailed configuration
2. Review [error logs](#troubleshooting) for specific issues
3. Test with `dry_run: true` to debug without side effects
4. Verify all required secrets are properly configured

## Examples Repository

See the [examples directory](examples/) for complete workflow files and configuration samples for different blog setups.