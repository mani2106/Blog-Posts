# Tweet Generator Demo Repository

This is a demonstration repository showing how to integrate the GitHub Tweet Thread Generator Action with a Jekyll blog. This example includes sample blog posts, configuration files, and workflow setups to help you understand how the action works.

## Repository Structure

```
demo-repository/
├── _posts/                          # Sample blog posts
│   ├── 2024-01-15-getting-started.md
│   ├── 2024-01-20-advanced-tips.md
│   └── 2024-01-25-case-study.md
├── _notebooks/                      # Sample Jupyter notebooks
│   └── 2024-01-30-data-analysis.ipynb
├── .github/
│   ├── workflows/
│   │   └── pages-with-tweets.yml    # GitHub Pages + Tweet generation
│   └── tweet-generator-config.yml   # Action configuration
├── .generated/                      # Generated content (created by action)
│   ├── writing-style-profile.json
│   ├── getting-started-thread.json
│   └── advanced-tips-thread.json
├── .posted/                         # Posted tweet metadata
│   └── getting-started.json
└── _config.yml                      # Jekyll configuration
```

## Sample Blog Posts

### Technical Tutorial Post

**File**: `_posts/2024-01-15-getting-started.md`

This post demonstrates how the action handles technical content with code examples and step-by-step instructions.

### Advanced Tips Post

**File**: `_posts/2024-01-20-advanced-tips.md`

Shows how the action processes more complex content with multiple sections and advanced concepts.

### Case Study Post

**File**: `_posts/2024-01-25-case-study.md`

Demonstrates processing of narrative content with personal experiences and lessons learned.

## Configuration Examples

### Basic Configuration

The demo uses a simple configuration in `.github/tweet-generator-config.yml`:

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
  max_tweets_per_thread: 8
```

### Workflow Integration

The GitHub Pages workflow in `.github/workflows/pages-with-tweets.yml` shows how to integrate tweet generation with your existing Jekyll build process.

## Generated Examples

### Style Profile

The action analyzes the sample posts to create a writing style profile:

```json
{
  "vocabulary_patterns": {
    "technical_terms": ["API", "configuration", "workflow", "integration"],
    "common_phrases": ["let's dive into", "here's how", "step by step"],
    "tone_indicators": ["friendly", "instructional", "encouraging"]
  },
  "content_structures": {
    "preferred_formats": ["numbered_lists", "code_blocks", "examples"],
    "average_paragraph_length": 3.2,
    "use_of_headers": "frequent"
  },
  "emoji_usage": {
    "frequency": "moderate",
    "preferred_emojis": ["🚀", "💡", "✅", "🔧"],
    "placement": "emphasis_and_bullets"
  }
}
```

### Sample Tweet Thread

Generated from the "Getting Started" post:

```json
{
  "post_slug": "getting-started",
  "tweets": [
    "🚀 Just discovered something that changed my entire development workflow...\n\nHere's how to set up automated tweet generation for your blog posts (thread 1/6)",
    "The problem: Writing engaging social media content takes hours away from actual coding.\n\nThe solution: Let AI analyze your writing style and create authentic tweet threads automatically ✨",
    "Here's what makes this different:\n\n✅ Learns YOUR writing voice\n✅ Maintains authenticity\n✅ Optimizes for engagement\n✅ Integrates with GitHub Pages\n\nNo more copy-paste social media 🎯",
    "The setup is surprisingly simple:\n\n1. Add the action to your workflow\n2. Configure your API keys\n3. Write blog posts as usual\n4. Get tweet threads automatically\n\nThat's it. Seriously.",
    "But here's the magic part...\n\nThe AI doesn't just summarize your content. It analyzes 50+ blog posts to understand:\n\n• Your vocabulary patterns\n• Tone preferences\n• Content structure\n• Emoji usage\n\nResult: Tweets that sound like YOU 🎭",
    "Want to try it? Check out the full setup guide:\n\n[Blog URL]\n\nWhat's your biggest challenge with social media content? Drop a comment below 👇\n\n#DevTools #Automation"
  ],
  "hashtags": ["#DevTools", "#Automation"],
  "engagement_score": 8.7,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

## How to Use This Demo

### 1. Fork and Setup

```bash
# Fork this repository
gh repo fork your-username/tweet-generator-demo

# Clone your fork
git clone https://github.com/your-username/tweet-generator-demo.git
cd tweet-generator-demo

# Set up secrets
gh secret set OPENROUTER_API_KEY --body "your-api-key"
gh secret set TWITTER_API_KEY --body "your-twitter-key"  # Optional
```

### 2. Customize Configuration

Edit `.github/tweet-generator-config.yml` to match your preferences:

```yaml
engagement:
  optimization_level: medium  # low, medium, high
  hook_variations: 2
  max_hashtags: 1

output:
  auto_post_enabled: true     # Enable auto-posting
  max_tweets_per_thread: 6
```

### 3. Add Your Content

Replace the sample posts in `_posts/` with your own content:

```markdown
---
title: "Your Blog Post Title"
date: 2024-01-15
categories: [tutorial, development]
summary: "Brief description for social media"
publish: true
auto_post: false  # Set to true for automatic posting
---

Your blog content here...
```

### 4. Test the Workflow

```bash
# Push changes to trigger the workflow
git add .
git commit -m "Add my blog post"
git push origin main

# Check the Actions tab for workflow execution
# Review generated PRs for tweet threads
```

## Expected Outputs

### Generated Files

After running the action, you'll see:

1. **Style Profile**: `.generated/writing-style-profile.json`
2. **Tweet Threads**: `.generated/{post-slug}-thread.json`
3. **Pull Requests**: For review before posting
4. **Posted Metadata**: `.posted/{post-slug}.json` (if auto-posted)

### Pull Request Example

The action creates PRs with:

- **Title**: "Generated tweet thread for: [Post Title]"
- **Body**: Preview of the thread, generation metadata, and review instructions
- **Files**: JSON thread file and any updates to style profile
- **Assignee**: Repository owner (you)

## Troubleshooting

### Common Issues

1. **No tweets generated**: Check that posts have `publish: true` in frontmatter
2. **API errors**: Verify your OpenRouter API key is valid
3. **Style analysis fails**: Ensure you have at least 3-5 blog posts for analysis
4. **Workflow doesn't trigger**: Check that the action path is correct

### Debug Mode

Enable debug logging by adding to your workflow:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### Getting Help

- Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Review the [FAQ](../FAQ.md)
- Open an issue with the `demo-repository` label

## Customization Ideas

### Advanced Configurations

1. **Multi-language support**: Configure different models for different languages
2. **Category-specific styles**: Use different engagement levels per post category
3. **Scheduled posting**: Combine with scheduling actions for optimal timing
4. **Analytics integration**: Track performance of generated threads

### Workflow Enhancements

1. **A/B testing**: Generate multiple thread variations
2. **Content approval**: Add manual approval steps before posting
3. **Cross-platform**: Extend to LinkedIn, Instagram, etc.
4. **Performance monitoring**: Track engagement metrics

## Contributing to the Demo

Help improve this demo repository:

1. **Add more sample posts**: Different content types and styles
2. **Create configuration variants**: Show different use cases
3. **Improve documentation**: Clarify setup steps
4. **Add troubleshooting examples**: Common issues and solutions

## License

This demo repository is provided under the same license as the main action. Feel free to use it as a starting point for your own blog automation setup.

---

**Questions?** Open an issue or check out the main [Tweet Generator Action documentation](../README.md).