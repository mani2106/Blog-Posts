# Troubleshooting Guide

This guide helps you resolve common issues with the GitHub Tweet Thread Generator.

## Table of Contents

- [Setup Issues](#setup-issues)
- [Authentication Problems](#authentication-problems)
- [Content Generation Issues](#content-generation-issues)
- [API Errors](#api-errors)
- [Performance Issues](#performance-issues)
- [Output Problems](#output-problems)
- [Debugging Tips](#debugging-tips)

## Setup Issues

### Action Not Running

**Symptoms**: The tweet generator action doesn't execute in your workflow.

**Possible Causes & Solutions**:

1. **Workflow Trigger Issues**
   ```yaml
   # ❌ Wrong - action won't run on PR
   on:
     pull_request:
       branches: [ main ]

   # ✅ Correct - action runs on push to main
   on:
     push:
       branches: [ main ]
   ```

2. **Conditional Logic Problems**
   ```yaml
   # ❌ Wrong - condition prevents execution
   if: github.event_name == 'pull_request'

   # ✅ Correct - runs on main branch pushes
   if: github.ref == 'refs/heads/main'
   ```

3. **File Path Issues**
   ```yaml
   # ❌ Wrong - incorrect path
   uses: ./.github/actions/tweet-gen

   # ✅ Correct - proper path
   uses: ./.github/actions/tweet-generator
   ```

### Missing Dependencies

**Symptoms**: Python import errors or missing packages.

**Solution**: Ensure `requirements.txt` is present and contains all dependencies:

```txt
python-frontmatter>=1.0.0
httpx>=0.24.0
pydantic>=2.0.0
PyGithub>=1.58.0
tweepy>=4.14.0
nltk>=3.8.0
textstat>=0.7.0
emoji>=2.2.0
```

### Directory Structure Problems

**Symptoms**: "Action not found" or "Invalid action" errors.

**Required Structure**:
```
.github/
└── actions/
    └── tweet-generator/
        ├── action.yml
        ├── requirements.txt
        ├── generate_and_commit.py
        └── src/
            ├── __init__.py
            ├── content_detector.py
            ├── style_analyzer.py
            ├── ai_orchestrator.py
            ├── engagement_optimizer.py
            ├── content_validator.py
            └── output_manager.py
```

## Authentication Problems

### OpenRouter API Issues

**Error**: `"OpenRouter API authentication failed"`

**Solutions**:

1. **Check API Key Format**
   ```bash
   # API key should start with 'sk-or-'
   echo $OPENROUTER_API_KEY | grep "^sk-or-"
   ```

2. **Verify Secret Configuration**
   - Go to Repository Settings → Secrets and variables → Actions
   - Ensure `OPENROUTER_API_KEY` is set correctly
   - No extra spaces or characters

3. **Test API Key Manually**
   ```bash
   curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        https://openrouter.ai/api/v1/models
   ```

### GitHub Token Issues

**Error**: `"GitHub API authentication failed"`

**Solutions**:

1. **Check Token Permissions**
   - `GITHUB_TOKEN` should have `contents: write` and `pull-requests: write`
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```

2. **Verify Repository Settings**
   - Ensure Actions have permission to create PRs
   - Check branch protection rules

### Twitter API Problems

**Error**: `"Twitter authentication failed"`

**Solutions**:

1. **Verify All Required Credentials**
   ```yaml
   # All four are required for Twitter API v2
   secrets:
     TWITTER_API_KEY: "your_api_key"
     TWITTER_API_SECRET: "your_api_secret"
     TWITTER_ACCESS_TOKEN: "your_access_token"
     TWITTER_ACCESS_TOKEN_SECRET: "your_access_token_secret"
   ```

2. **Check API Version Compatibility**
   - Ensure you're using Twitter API v2
   - Verify app permissions include "Read and Write"

3. **Test Twitter Connection**
   ```python
   import tweepy

   client = tweepy.Client(
       consumer_key="your_api_key",
       consumer_secret="your_api_secret",
       access_token="your_access_token",
       access_token_secret="your_access_token_secret"
   )

   try:
       user = client.get_me()
       print(f"Connected as: {user.data.username}")
   except Exception as e:
       print(f"Error: {e}")
   ```

## Content Generation Issues

### No Posts Found

**Error**: `"No posts found to process"`

**Solutions**:

1. **Check Frontmatter Format**
   ```yaml
   ---
   title: "My Post Title"
   publish: true  # This must be present and true
   ---
   ```

2. **Verify File Locations**
   - Posts should be in `_posts/` directory
   - Notebooks should be in `_notebooks/` directory
   - Files should have `.md` or `.ipynb` extensions

3. **Check Git Changes**
   ```bash
   # Verify files are actually changed
   git diff --name-only HEAD~1 HEAD
   ```

### Style Analysis Failures

**Error**: `"Insufficient content for style analysis"`

**Solutions**:

1. **Ensure Minimum Content**
   - Need at least 3 published posts
   - Posts should have substantial content (>500 words recommended)

2. **Check Content Quality**
   ```yaml
   # Posts should have proper frontmatter
   ---
   title: "Descriptive Title"
   categories: [category1, category2]
   description: "Brief description"
   publish: true
   ---

   # Substantial content here...
   ```

3. **Manual Style Profile Creation**
   ```bash
   # Force regeneration of style profile
   rm .generated/writing-style-profile.json
   # Re-run the action
   ```

### AI Generation Failures

**Error**: `"AI model failed to generate content"`

**Solutions**:

1. **Check Model Availability**
   ```bash
   # Test model access
   curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model": "anthropic/claude-3-haiku", "messages": [{"role": "user", "content": "test"}]}' \
        https://openrouter.ai/api/v1/chat/completions
   ```

2. **Try Alternative Models**
   ```yaml
   env:
     OPENROUTER_MODEL: "openai/gpt-3.5-turbo"  # Fallback model
   ```

3. **Reduce Content Complexity**
   - Shorter blog posts may work better
   - Simpler content structure
   - Clear, well-formatted markdown

## API Errors

### Rate Limiting

**Error**: `"Rate limit exceeded"`

**Solutions**:

1. **Implement Delays**
   ```yaml
   env:
     API_RETRY_DELAY: "30"  # seconds between retries
     MAX_RETRIES: "3"
   ```

2. **Reduce Concurrent Requests**
   ```yaml
   env:
     MAX_CONCURRENT_POSTS: "1"  # Process one post at a time
   ```

3. **Use Different Models**
   ```yaml
   env:
     OPENROUTER_MODEL: "anthropic/claude-3-haiku"  # Faster, cheaper model
   ```

### Network Timeouts

**Error**: `"Request timeout"`

**Solutions**:

1. **Increase Timeout Values**
   ```yaml
   env:
     API_TIMEOUT: "120"  # seconds
   ```

2. **Check Network Connectivity**
   ```bash
   # Test connectivity to APIs
   curl -I https://openrouter.ai/api/v1/models
   curl -I https://api.twitter.com/2/users/me
   ```

### Invalid Responses

**Error**: `"Invalid JSON response from API"`

**Solutions**:

1. **Enable Debug Logging**
   ```yaml
   env:
     LOGGING_LEVEL: "DEBUG"
   ```

2. **Check API Status**
   - Visit OpenRouter status page
   - Check Twitter API status

3. **Validate Request Format**
   ```python
   # Ensure proper request structure
   {
       "model": "anthropic/claude-3-haiku",
       "messages": [
           {"role": "system", "content": "system_prompt"},
           {"role": "user", "content": "user_prompt"}
       ],
       "max_tokens": 4000
   }
   ```

## Performance Issues

### Slow Execution

**Symptoms**: Action takes longer than 10 minutes to complete.

**Solutions**:

1. **Optimize Content Processing**
   ```yaml
   env:
     MAX_POSTS_PER_RUN: "5"  # Limit posts processed
     STYLE_ANALYSIS_CACHE: "true"  # Cache style analysis
   ```

2. **Use Faster Models**
   ```yaml
   env:
     OPENROUTER_MODEL: "anthropic/claude-3-haiku"  # Faster model
   ```

3. **Parallel Processing**
   ```yaml
   env:
     ENABLE_PARALLEL_PROCESSING: "true"
     MAX_WORKERS: "3"
   ```

### Memory Issues

**Error**: `"Out of memory"` or workflow killed

**Solutions**:

1. **Reduce Memory Usage**
   ```yaml
   env:
     BATCH_SIZE: "1"  # Process one post at a time
     CLEAR_CACHE: "true"  # Clear caches between posts
   ```

2. **Optimize Content Loading**
   ```python
   # Stream large files instead of loading entirely
   # Limit content analysis to recent posts only
   ```

### GitHub Actions Limits

**Error**: Workflow exceeds time or resource limits

**Solutions**:

1. **Split Processing**
   ```yaml
   # Create separate workflow for tweet generation
   name: Generate Tweets
   on:
     workflow_run:
       workflows: ["Build and Deploy"]
       types: [completed]
   ```

2. **Use Self-Hosted Runners**
   ```yaml
   runs-on: self-hosted  # For more resources
   ```

## Output Problems

### PR Creation Failures

**Error**: `"Failed to create pull request"`

**Solutions**:

1. **Check Repository Permissions**
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```

2. **Verify Branch Protection**
   - Ensure Actions can create PRs
   - Check required status checks

3. **Manual PR Creation**
   ```bash
   # If automated PR fails, create manually
   git checkout -b tweet-threads-$(date +%Y%m%d)
   git add .generated/ .posted/
   git commit -m "Add generated tweet threads"
   git push origin tweet-threads-$(date +%Y%m%d)
   ```

### File Permission Issues

**Error**: `"Permission denied"` when writing files

**Solutions**:

1. **Check Directory Permissions**
   ```bash
   # Ensure directories are writable
   mkdir -p .generated .posted
   chmod 755 .generated .posted
   ```

2. **Verify Git Configuration**
   ```yaml
   - name: Configure Git
     run: |
       git config --global user.name "github-actions[bot]"
       git config --global user.email "github-actions[bot]@users.noreply.github.com"
   ```

### Invalid Output Format

**Error**: Generated files are malformed or empty

**Solutions**:

1. **Validate JSON Output**
   ```bash
   # Check generated files
   python -m json.tool .generated/my-post-thread.json
   ```

2. **Enable Validation**
   ```yaml
   env:
     STRICT_VALIDATION: "true"
     VALIDATE_OUTPUT: "true"
   ```

## Debugging Tips

### Enable Debug Logging

```yaml
env:
  LOGGING_LEVEL: "DEBUG"
  INCLUDE_API_RESPONSES: "true"
  SAVE_INTERMEDIATE_FILES: "true"
```

### Test Locally

```bash
# Set up local environment
export OPENROUTER_API_KEY="your_key"
export GITHUB_TOKEN="your_token"
export DRY_RUN_MODE="true"

# Run the action locally
python .github/actions/tweet-generator/generate_and_commit.py
```

### Check Action Logs

1. Go to Actions tab in your repository
2. Click on the failed workflow run
3. Expand the "Generate tweet threads" step
4. Look for error messages and stack traces

### Validate Configuration

```python
# Test configuration loading
from src.config import load_config

try:
    config = load_config()
    print("Configuration loaded successfully")
    print(f"Model: {config.openrouter_model}")
    print(f"Auto-post enabled: {config.auto_post_enabled}")
except Exception as e:
    print(f"Configuration error: {e}")
```

### Test Individual Components

```python
# Test content detection
from src.content_detector import ContentDetector

detector = ContentDetector()
posts = detector.detect_changed_posts()
print(f"Found {len(posts)} posts to process")

# Test style analysis
from src.style_analyzer import StyleAnalyzer

analyzer = StyleAnalyzer()
profile = analyzer.build_style_profile("_posts", "_notebooks")
print(f"Style profile created with {len(profile.vocabulary_patterns)} patterns")
```

## Getting Help

If you're still experiencing issues:

1. **Check the FAQ** in the main README
2. **Search existing issues** in the repository
3. **Create a new issue** with:
   - Complete error messages
   - Workflow configuration
   - Repository structure
   - Steps to reproduce

4. **Include debug information**:
   ```yaml
   # Add this to your workflow for debugging
   - name: Debug Information
     run: |
       echo "Repository: ${{ github.repository }}"
       echo "Branch: ${{ github.ref }}"
       echo "Event: ${{ github.event_name }}"
       ls -la _posts/ || echo "No _posts directory"
       ls -la _notebooks/ || echo "No _notebooks directory"
   ```

## Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `AUTH_001` | OpenRouter API key invalid | Check API key format and permissions |
| `AUTH_002` | GitHub token insufficient permissions | Add `contents: write` and `pull-requests: write` |
| `AUTH_003` | Twitter API authentication failed | Verify all four Twitter credentials |
| `CONTENT_001` | No posts found to process | Check `publish: true` in frontmatter |
| `CONTENT_002` | Style analysis failed | Ensure minimum 3 posts with substantial content |
| `API_001` | Rate limit exceeded | Reduce request frequency or use different model |
| `API_002` | Model not available | Try alternative model or check OpenRouter status |
| `OUTPUT_001` | PR creation failed | Check repository permissions and branch protection |
| `OUTPUT_002` | File write permission denied | Verify directory permissions and Git configuration |

---

**Still need help?** Open an issue with the error code and we'll help you resolve it quickly.