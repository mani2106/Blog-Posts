# Migration Guide

This guide helps you migrate between different versions of the GitHub Tweet Thread Generator Action and upgrade your existing setup.

## Version Migration Guides

### Migrating to v2.0.0 from v1.x.x

**Release Date**: TBD
**Migration Difficulty**: Medium
**Estimated Time**: 30-60 minutes

#### Breaking Changes

1. **Configuration File Format**
   - **Old**: Environment variables only
   - **New**: YAML configuration file with environment variable fallbacks

2. **Action Input Parameters**
   - **Removed**: `engagement_level` input parameter
   - **Changed**: `dry_run` → `dry_run_mode`
   - **Added**: `config_file` parameter

3. **Output File Structure**
   - **Changed**: Thread files now include additional metadata
   - **New**: Style profile versioning

#### Step-by-Step Migration

##### 1. Update Workflow File

**Before (v1.x.x)**:
```yaml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator@v1
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    engagement_level: 'high'
    dry_run: 'false'
```

**After (v2.0.0)**:
```yaml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator@v2
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    config_file: '.github/tweet-generator-config.yml'
    dry_run_mode: 'false'
```

##### 2. Create Configuration File

Create `.github/tweet-generator-config.yml`:

```yaml
# Migrate your old environment variables to this format
engagement:
  optimization_level: high  # Was 'engagement_level' input

output:
  dry_run_mode: false      # Was 'dry_run' input
  auto_post_enabled: false # New feature
```

##### 3. Update Environment Variables

**Removed Variables** (now in config file):
- `ENGAGEMENT_LEVEL`
- `MAX_TWEETS_PER_THREAD`
- `AUTO_POST_ENABLED`

**New Variables**:
- `TWITTER_API_KEY` (optional, for auto-posting)
- `TWITTER_API_SECRET` (optional, for auto-posting)

##### 4. Migrate Generated Files

The action will automatically migrate existing files:

- `.generated/writing-style-profile.json` → Updated with version info
- `.generated/*-thread.json` → Backward compatible, new metadata added

##### 5. Test Migration

```bash
# Test with dry run first
git add .github/tweet-generator-config.yml
git commit -m "Add v2.0 configuration"
git push origin main

# Check Actions tab for successful execution
# Review any generated PRs for format changes
```

#### Rollback Plan

If migration fails, you can rollback:

```yaml
# Temporarily use v1.x.x
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator@v1.9.0
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    engagement_level: 'high'
```

### Migrating to v1.5.0 from v1.0.x-v1.4.x

**Release Date**: 2024-01-15
**Migration Difficulty**: Easy
**Estimated Time**: 10-15 minutes

#### Changes

1. **New Features**
   - Auto-posting to Twitter (optional)
   - Enhanced style analysis
   - Improved error handling

2. **New Input Parameters**
   - `twitter_api_key` (optional)
   - `twitter_api_secret` (optional)

#### Migration Steps

##### 1. Update Action Version

```yaml
# Change from v1.0, v1.1, v1.2, v1.3, or v1.4
uses: ./.github/actions/tweet-generator@v1.5
```

##### 2. Add Twitter Credentials (Optional)

If you want auto-posting:

```bash
gh secret set TWITTER_API_KEY --body "your-twitter-api-key"
gh secret set TWITTER_API_SECRET --body "your-twitter-api-secret"
```

Update workflow:
```yaml
- name: Generate tweet threads
  uses: ./.github/actions/tweet-generator@v1.5
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    twitter_api_key: ${{ secrets.TWITTER_API_KEY }}      # New
    twitter_api_secret: ${{ secrets.TWITTER_API_SECRET }}  # New
```

##### 3. Update Blog Post Frontmatter (Optional)

Add auto-posting control to your posts:

```yaml
---
title: "Your Post Title"
auto_post: true  # New: Enable auto-posting for this post
---
```

## General Migration Best Practices

### Pre-Migration Checklist

- [ ] **Backup existing configuration** and generated files
- [ ] **Review changelog** for your target version
- [ ] **Test in a fork** or separate repository first
- [ ] **Check API compatibility** (OpenRouter, Twitter, GitHub)
- [ ] **Verify secrets** are properly configured
- [ ] **Update documentation** references

### Migration Testing Strategy

#### 1. Fork Testing

```bash
# Create a test fork
gh repo fork your-username/your-blog --clone

# Test migration in fork
cd your-blog
# Apply migration changes
git push origin main

# Verify workflow execution
gh run list --limit 5
```

#### 2. Dry Run Testing

Always test with dry run first:

```yaml
- name: Test migration
  uses: ./.github/actions/tweet-generator@v2
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    dry_run_mode: 'true'  # Test without creating PRs
```

#### 3. Gradual Rollout

For production sites:

1. **Week 1**: Deploy to staging/test branch
2. **Week 2**: Deploy to main with dry run enabled
3. **Week 3**: Enable full functionality
4. **Week 4**: Monitor and optimize

### Common Migration Issues

#### Issue: Configuration Not Found

**Error**: `Configuration file not found: .github/tweet-generator-config.yml`

**Solution**:
```bash
# Create minimal config file
cat > .github/tweet-generator-config.yml << EOF
engagement:
  optimization_level: medium
output:
  auto_post_enabled: false
EOF
```

#### Issue: API Key Format Changed

**Error**: `Invalid API key format`

**Solution**: Check the new format requirements in the changelog and update your secrets accordingly.

#### Issue: Generated Files Incompatible

**Error**: `Cannot parse existing style profile`

**Solution**: Delete existing generated files to force regeneration:
```bash
rm -rf .generated/
git add .generated/
git commit -m "Reset generated files for migration"
```

#### Issue: Workflow Permissions

**Error**: `Permission denied when creating PR`

**Solution**: Update workflow permissions:
```yaml
permissions:
  contents: read
  pull-requests: write  # Required for PR creation
  issues: write         # Required for issue creation
```

### Post-Migration Validation

#### 1. Functionality Testing

- [ ] **Style analysis** runs successfully
- [ ] **Thread generation** produces expected output
- [ ] **PR creation** works correctly
- [ ] **Auto-posting** functions (if enabled)
- [ ] **Error handling** behaves properly

#### 2. Performance Validation

Monitor these metrics after migration:

```bash
# Check workflow execution times
gh run list --json conclusion,createdAt,updatedAt

# Monitor API usage
# Check OpenRouter dashboard for usage patterns

# Validate output quality
# Review generated threads for consistency
```

#### 3. Rollback Triggers

Rollback if you observe:

- **Execution failures** > 20% of runs
- **Generation quality** significantly decreased
- **Performance degradation** > 50% slower
- **API errors** > 10% of requests

## Platform-Specific Migrations

### Jekyll to Hugo

If migrating from Jekyll to Hugo:

#### 1. Update Content Detection

Hugo uses different frontmatter and directory structure:

```yaml
# Add to config
content:
  posts_directory: "content/posts"  # Hugo default
  notebooks_directory: "content/notebooks"
```

#### 2. Frontmatter Mapping

```yaml
# Jekyll frontmatter
---
layout: post
title: "My Post"
date: 2024-01-15
categories: [tutorial]
---

# Hugo frontmatter
---
title: "My Post"
date: 2024-01-15
categories: ["tutorial"]
draft: false
---
```

#### 3. URL Structure

Update canonical URL generation:

```yaml
# In config file
url_generation:
  base_url: "https://yourblog.com"
  path_format: "/posts/{slug}/"  # Hugo format
```

### GitHub Pages to Netlify

When migrating hosting platforms:

#### 1. Update Workflow Triggers

```yaml
# For Netlify deployment
on:
  push:
    branches: [ main ]
  # Remove GitHub Pages specific triggers
```

#### 2. Adjust File Paths

```yaml
# Update paths for Netlify build
content:
  build_directory: "public"     # Netlify default
  posts_directory: "content"
```

#### 3. Environment Variables

```bash
# Netlify environment variables
OPENROUTER_API_KEY=your-key
TWITTER_API_KEY=your-key
# Add to Netlify dashboard
```

## Troubleshooting Migration Issues

### Debug Mode

Enable debug mode during migration:

```yaml
- name: Generate tweet threads (debug)
  uses: ./.github/actions/tweet-generator@v2
  with:
    openrouter_api_key: ${{ secrets.OPENROUTER_API_KEY }}
    debug_mode: 'true'
  env:
    ACTIONS_STEP_DEBUG: true
```

### Log Analysis

Check logs for common issues:

```bash
# Download workflow logs
gh run download [run-id]

# Search for specific errors
grep -r "ERROR" downloaded-logs/
grep -r "Configuration" downloaded-logs/
```

### Support Resources

If you encounter issues:

1. **Check the FAQ**: [FAQ.md](FAQ.md)
2. **Review troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Search existing issues**: GitHub Issues tab
4. **Create new issue**: Use migration issue template

### Migration Issue Template

When reporting migration issues:

```markdown
## Migration Issue Report

**From Version**: v1.4.0
**To Version**: v2.0.0
**Migration Step**: Configuration file creation

**Error Message**:
```
[Paste error message here]
```

**Configuration**:
```yaml
[Paste relevant config here]
```

**Expected Behavior**:
[Describe what should happen]

**Actual Behavior**:
[Describe what actually happened]

**Additional Context**:
- Repository type: Jekyll/Hugo/Other
- Hosting platform: GitHub Pages/Netlify/Other
- Previous working version: v1.4.0
```

## Version Compatibility Matrix

| Feature | v1.0 | v1.1 | v1.2 | v1.3 | v1.4 | v1.5 | v2.0 |
|---------|------|------|------|------|------|------|------|
| Basic thread generation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Style analysis | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| PR creation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auto-posting | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| YAML configuration | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Multi-model support | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Enhanced safety | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Performance optimization | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |

## Getting Help

### Community Support

- **GitHub Discussions**: Ask questions and share experiences
- **Discord Server**: Real-time help and community chat
- **Stack Overflow**: Tag questions with `github-tweet-generator`

### Professional Support

For enterprise users:

- **Priority Support**: Dedicated migration assistance
- **Custom Migration**: Tailored migration plans
- **Training Sessions**: Team onboarding and best practices

### Documentation

- **API Reference**: [API.md](API.md)
- **Configuration Guide**: [README.md](README.md)
- **Examples**: [examples/](examples/)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Need help with migration?** Open an issue with the `migration` label and we'll help you through the process.