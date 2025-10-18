# Auto-Posting Functionality

This document describes the auto-posting functionality for the GitHub Action Tweet Thread Generator.

## Overview

The auto-posting feature allows the system to automatically post generated tweet threads to Twitter/X when certain conditions are met. It includes comprehensive controls, duplicate detection, and graceful fallback to PR creation when auto-posting fails.

## Components

### TwitterClient (`twitter_client.py`)

Handles Twitter API v2 integration with the following features:

- **Authentication**: Supports Twitter API v2 with OAuth 1.0a
- **Thread Posting**: Posts complete tweet threads with proper reply chaining
- **Rate Limiting**: Handles Twitter's rate limits (300 tweets per 15 minutes)
- **Error Handling**: Comprehensive error handling with retries and exponential backoff
- **Validation**: Pre-posting validation of character limits and thread structure

### AutoPoster (`auto_poster.py`)

Manages auto-posting logic and controls:

- **Duplicate Detection**: Prevents re-posting using `.posted/<slug>.json` files
- **Auto-Post Controls**: Checks `auto_post` frontmatter flag and global settings
- **Metadata Storage**: Saves posting metadata with tweet IDs and timestamps
- **Graceful Fallback**: Falls back to PR creation when auto-posting fails
- **Statistics**: Tracks posting success rates and thread metrics

## Configuration

### Environment Variables

Required for auto-posting:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Auto-posting Controls
AUTO_POST_ENABLED=true
DRY_RUN=false  # Set to true for testing without actual posting
```

### Blog Post Configuration

Enable auto-posting for individual posts by adding to frontmatter:

```yaml
---
title: "My Blog Post"
auto_post: true
publish: true
---
```

## Auto-Posting Logic

The system will auto-post a thread if ALL conditions are met:

1. ✅ Global auto-posting is enabled (`AUTO_POST_ENABLED=true`)
2. ✅ Not running in dry-run mode (`DRY_RUN=false`)
3. ✅ Post has `auto_post: true` in frontmatter
4. ✅ Post has not been previously posted
5. ✅ Twitter API credentials are configured
6. ✅ Thread passes validation (character limits, safety checks)

If any condition fails, the system will create a PR for manual review instead.

## Posted Metadata

When a thread is successfully posted, metadata is saved to `.posted/<slug>.json`:

```json
{
  "post_slug": "my-blog-post",
  "success": true,
  "tweet_ids": ["1234567890", "1234567891", "1234567892"],
  "platform": "twitter",
  "posted_at": "2023-12-01T10:30:00Z",
  "thread_length": 3,
  "created_at": "2023-12-01T10:30:05Z"
}
```

## Error Handling

### Twitter API Errors

- **Rate Limits**: Automatic waiting with exponential backoff
- **Authentication Errors**: Clear error messages, graceful fallback to PR
- **Network Errors**: Retry with exponential backoff (max 3 attempts)
- **Invalid Content**: Content validation before posting

### Partial Posting Failures

If a thread is partially posted (some tweets succeed, others fail):

1. System logs the partial failure
2. Optionally attempts cleanup (delete posted tweets)
3. Falls back to PR creation for manual handling
4. Saves metadata indicating partial failure

## Safety Features

### Content Validation

Before posting, all content is validated for:

- Character limits (280 chars per tweet)
- Profanity and inappropriate content
- Proper thread structure and sequencing
- Required engagement elements

### Duplicate Prevention

- Checks `.posted/<slug>.json` files before posting
- Prevents accidental re-posting of the same content
- Maintains posting history for audit purposes

### Dry-Run Mode

Enable dry-run mode for testing:

```bash
DRY_RUN=true
```

In dry-run mode:
- No actual tweets are posted
- All validation and logic is executed
- Mock tweet IDs are returned for testing
- Safe for development and testing

## Usage Examples

### Basic Auto-Posting Setup

1. Configure Twitter API credentials in GitHub Secrets
2. Enable auto-posting: `AUTO_POST_ENABLED=true`
3. Add `auto_post: true` to blog post frontmatter
4. Push changes to trigger the workflow

### Manual Review Workflow

1. Set `AUTO_POST_ENABLED=false` or omit `auto_post: true`
2. System generates thread and creates PR
3. Review thread content in PR description
4. Merge PR to save draft (manual posting required)

### Testing Setup

1. Set `DRY_RUN=true`
2. Configure test credentials (can be dummy values)
3. Run workflow to test logic without actual posting

## Monitoring and Statistics

### Posting Statistics

Get posting statistics programmatically:

```python
from auto_poster import AutoPoster
from models import GeneratorConfig

config = GeneratorConfig.from_env()
auto_poster = AutoPoster(config)

stats = auto_poster.get_posting_statistics()
print(f"Success rate: {stats['successful_posts']}/{stats['total_posts']}")
```

### Posted Threads List

List all posted threads:

```python
threads = auto_poster.list_posted_threads()
for thread in threads:
    print(f"Posted: {thread['post_slug']} at {thread['posted_at']}")
```

## Troubleshooting

### Common Issues

1. **"Auto-posting skipped: Twitter API credentials are not configured"**
   - Ensure all 4 Twitter API credentials are set in environment variables

2. **"Auto-posting skipped: Post does not have auto_post: true in frontmatter"**
   - Add `auto_post: true` to the blog post's frontmatter

3. **"Auto-posting skipped: Auto-posting is globally disabled"**
   - Set `AUTO_POST_ENABLED=true` in environment variables

4. **"Twitter API error: Invalid or expired token"**
   - Verify Twitter API credentials are correct and not expired
   - Check Twitter Developer Portal for API access status

### Validation Setup

Run setup validation:

```python
issues = auto_poster.validate_auto_posting_setup()
if issues:
    print("Setup issues found:")
    for issue in issues:
        print(f"- {issue}")
```

## Security Considerations

- Twitter API credentials are never logged or exposed
- All API calls use secure HTTPS connections
- Posted metadata contains no sensitive information
- Dry-run mode prevents accidental posting during development

## Rate Limits

Twitter API v2 rate limits:
- **Tweet Creation**: 300 tweets per 15-minute window
- **Thread Posting**: Automatic spacing between tweets (1 second minimum)
- **Rate Limit Handling**: Automatic waiting when limits are reached

The system respects these limits and will wait when necessary to avoid API errors.