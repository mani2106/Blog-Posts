# Frequently Asked Questions (FAQ)

## General Questions

### What is the GitHub Tweet Thread Generator?

The GitHub Tweet Thread Generator is a GitHub Action that automatically creates engaging tweet threads from your blog posts using AI. It analyzes your writing style, applies proven engagement techniques, and creates threads optimized for social media sharing.

### How does it work?

1. **Content Detection**: Scans for new or updated blog posts in your repository
2. **Style Analysis**: Learns your writing style from existing posts
3. **AI Generation**: Uses OpenRouter API with multiple AI models to create threads
4. **Engagement Optimization**: Applies proven social media techniques
5. **Review Process**: Creates pull requests for human review before posting

### What blog platforms are supported?

- Jekyll (GitHub Pages)
- Fastpages
- Hugo (with proper frontmatter)
- Any markdown-based blog with frontmatter
- Jupyter notebooks in `_notebooks` directory

### Do I need coding experience to use this?

No! The action is designed to work with minimal setup. You just need to:
1. Copy the action files to your repository
2. Add your API keys to GitHub Secrets
3. Add a step to your existing workflow

## Setup and Configuration

### What API keys do I need?

**Required:**
- `OPENROUTER_API_KEY`: For AI content generation

**Optional (for auto-posting):**
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`

### How do I get an OpenRouter API key?

1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Go to your dashboard
4. Generate an API key
5. Add it to your GitHub repository secrets as `OPENROUTER_API_KEY`

### How much does it cost to run?

**OpenRouter API costs** (approximate):
- Claude-3-Haiku: ~$0.01-0.05 per thread
- Claude-3-Sonnet: ~$0.05-0.15 per thread
- GPT-3.5-Turbo: ~$0.01-0.03 per thread

**GitHub Actions**: Free for public repositories, included in private repository minutes

**Twitter API**: Free tier available, paid plans for higher usage

### Can I use it without auto-posting?

Yes! The action works great for generating tweet drafts that you can review and post manually. Just set `auto_post_enabled: false` in your configuration.

### How do I customize the generated content?

You can customize through:
- Configuration files (`.github/tweet-generator-config.yml`)
- Environment variables
- Custom hook templates
- Engagement optimization levels
- Model selection

## Content and Style

### How does style analysis work?

The action analyzes your existing blog posts to learn:
- Vocabulary patterns and common phrases
- Tone and sentiment preferences
- Content structure and organization
- Technical terminology usage
- Emoji and formatting preferences

This creates a unique style profile saved as `.generated/writing-style-profile.json`.

### What if I don't have enough existing content?

You need at least 3 published blog posts for effective style analysis. If you have fewer:
- The action will use a generic professional tone
- Style analysis will improve as you publish more content
- You can manually create a basic style profile

### Can I control the tone and style?

Yes! You can:
- Set engagement optimization levels (low/medium/high)
- Customize hook templates
- Configure power words and psychological triggers
- Adjust technical terminology preferences
- Set emoji usage preferences

### How are hashtags selected?

Hashtags are selected based on:
- Post categories and tags
- Content analysis
- Trending topics (when configured)
- Technical terminology detected
- Maximum of 1-2 hashtags per thread (configurable)

## Technical Questions

### Which AI models are supported?

**OpenRouter Models:**
- Anthropic Claude (3-Haiku, 3-Sonnet, 3-Opus)
- OpenAI GPT (3.5-Turbo, 4, 4-Turbo)
- Google Gemini Pro
- Meta Llama models
- Mistral models

**Model Routing:**
- Planning: Fast model for structure (Claude-3-Haiku)
- Creative: High-quality model for hooks (Claude-3-Sonnet)
- Verification: Efficient model for validation (Claude-3-Haiku)

### How does the action detect new posts?

The action uses `git diff` to compare the current commit with the main branch, looking for:
- New files in `_posts` or `_notebooks` directories
- Modified existing posts
- Posts with `publish: true` in frontmatter

### What happens if the AI generation fails?

The action includes comprehensive error handling:
- Automatic retries with exponential backoff
- Fallback to simpler models
- Graceful degradation (creates PR without auto-posting)
- Detailed error logging for debugging

### Can I run this locally for testing?

Yes! Set up your environment:

```bash
export OPENROUTER_API_KEY="your-key"
export DRY_RUN_MODE="true"
export LOGGING_LEVEL="DEBUG"

python .github/actions/tweet-generator/generate_and_commit.py
```

### How do I handle rate limits?

The action includes built-in rate limiting:
- Configurable delays between requests
- Exponential backoff on rate limit errors
- Conservative default settings
- Monitoring and logging of API usage

## Content Safety and Quality

### How does content filtering work?

The action includes multiple safety layers:
- **Profanity detection**: Filters inappropriate language
- **Content safety**: Checks for hate speech and spam
- **Numeric claims**: Flags statistics for manual review
- **Technical accuracy**: Warns about potentially outdated information
- **Character limits**: Enforces Twitter's 280-character limit

### Can I review content before it's posted?

Yes! The action creates pull requests with:
- Complete thread preview
- Character counts for each tweet
- Hook variations to choose from
- Generation metadata
- Review checklist

### What if I don't like the generated content?

You have several options:
- Edit the generated JSON files directly
- Regenerate with different settings
- Use different hook variations provided
- Adjust your configuration for future posts
- Post manually with your own content

### How accurate is the technical content?

The AI models are trained on vast datasets but can make mistakes. Always review technical content for:
- Accuracy of code examples
- Current best practices
- Version-specific information
- Security considerations

## Workflow Integration

### How do I add this to my existing workflow?

Add this step to your `.github/workflows/pages.yml`:

```yaml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
  if: github.ref == 'refs/heads/main'
```

### Can I use this with multiple blogs?

Yes! You can:
- Use different configurations for different content types
- Set up matrix builds for multiple sites
- Use different output directories
- Configure separate Twitter accounts

### What permissions does the action need?

```yaml
permissions:
  contents: write          # To commit generated files
  pull-requests: write     # To create review PRs
  pages: write            # If deploying to GitHub Pages
  id-token: write         # For GitHub Pages deployment
```

### How do I prevent the action from running on certain commits?

Use `[skip ci]` in your commit message, or add conditions:

```yaml
if: github.ref == 'refs/heads/main' && !contains(github.event.head_commit.message, '[skip tweet]')
```

## Troubleshooting

### The action isn't running

Check:
- Workflow file syntax and indentation
- Required permissions are set
- Conditional logic (`if` statements)
- Repository settings allow Actions

### No posts are being processed

Verify:
- Posts have `publish: true` in frontmatter
- Posts are in `_posts` or `_notebooks` directories
- Git diff detects the changes
- File extensions are `.md` or `.ipynb`

### API authentication errors

Common issues:
- API key format (should start with `sk-or-` for OpenRouter)
- Expired or invalid keys
- Incorrect secret names in GitHub
- Missing required Twitter credentials

### Generated content quality issues

Try:
- Using higher-quality models (Claude-3-Sonnet vs Haiku)
- Adjusting engagement optimization level
- Providing more detailed post content
- Customizing hook templates
- Reviewing and updating style profile

### Performance issues

Optimize by:
- Using faster models for planning
- Reducing concurrent requests
- Enabling caching
- Processing fewer posts per run
- Using incremental style analysis

## Best Practices

### Writing Blog Posts for Better Threads

**Frontmatter:**
```yaml
---
title: "Clear, Descriptive Title"
description: "Brief summary for context"
categories: [relevant, categories]
publish: true
auto_post: false  # Start with manual review
---
```

**Content Structure:**
- Clear introduction with value proposition
- Well-organized sections with headers
- Key takeaways and actionable insights
- Concrete examples and code snippets
- Strong conclusion with call-to-action

### Optimizing for Engagement

**Hook Optimization:**
- Start with curiosity gaps or contrarian takes
- Use specific numbers and timeframes
- Promise clear value or learning outcomes
- Create pattern interrupts

**Thread Structure:**
- Use numbered sequences (1/n format)
- Include cliffhangers between tweets
- Add visual hierarchy with emojis and formatting
- End with engaging questions or CTAs

### Security Best Practices

**API Key Management:**
- Use GitHub Secrets, never commit keys
- Rotate keys regularly
- Use least-privilege access
- Monitor API usage and costs

**Content Safety:**
- Always review generated content
- Enable all safety filters
- Be cautious with auto-posting
- Monitor for inappropriate content

### Monitoring and Maintenance

**Regular Tasks:**
- Review generated content quality
- Monitor API costs and usage
- Update model configurations
- Clean up old generated files
- Check for action updates

**Performance Monitoring:**
- Track generation success rates
- Monitor API response times
- Review error logs regularly
- Optimize based on usage patterns

## Advanced Usage

### Custom Model Configurations

```yaml
models:
  technical_content: "anthropic/claude-3-sonnet"
  personal_content: "anthropic/claude-3-haiku"
  announcement_content: "openai/gpt-4-turbo"
```

### Multi-Language Support

The action can work with content in different languages by:
- Configuring language-specific models
- Adjusting style analysis for different languages
- Using appropriate hashtags for target audiences

### Integration with Other Tools

**Analytics Integration:**
- Track thread performance
- A/B test different hook types
- Monitor engagement metrics
- Optimize based on data

**Content Management:**
- Integrate with CMS systems
- Automate content workflows
- Schedule posts across platforms
- Manage content calendars

## Getting Help

### Where can I get support?

1. **Documentation**: Check the README and API docs
2. **Troubleshooting Guide**: Review common issues and solutions
3. **GitHub Issues**: Search existing issues or create new ones
4. **Discussions**: Join community discussions
5. **Examples**: Review example configurations and workflows

### How do I report bugs?

When reporting bugs, include:
- Complete error messages and logs
- Your workflow configuration
- Repository structure
- Steps to reproduce the issue
- Expected vs actual behavior

### How do I request features?

Feature requests should include:
- Clear description of the desired functionality
- Use case and benefits
- Proposed implementation approach
- Willingness to contribute or test

### How do I contribute?

Contributions are welcome! You can:
- Fix bugs and improve documentation
- Add new features and enhancements
- Create example configurations
- Help with testing and validation
- Improve error handling and user experience

---

**Still have questions?** Check the [GitHub repository](https://github.com/yourusername/tweet-generator) or open an issue for help!