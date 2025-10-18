# Versioning Strategy

## Overview

The GitHub Tweet Thread Generator Action follows [Semantic Versioning (SemVer)](https://semver.org/) for version management. This document outlines our versioning strategy, release process, and compatibility guarantees.

## Version Format

We use the format `MAJOR.MINOR.PATCH[-PRERELEASE]`:

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backwards-compatible functionality additions
- **PATCH**: Incremented for backwards-compatible bug fixes
- **PRERELEASE**: Optional suffix for pre-release versions (alpha, beta, rc)

### Examples

- `v1.0.0` - Stable release
- `v1.1.0` - Minor feature addition
- `v1.0.1` - Bug fix
- `v2.0.0` - Breaking changes
- `v1.1.0-beta1` - Pre-release version

## Release Types

### Stable Releases

Stable releases are production-ready versions that have passed all tests and validation:

- **Major Releases** (`v2.0.0`): Contain breaking changes, require migration
- **Minor Releases** (`v1.1.0`): Add new features while maintaining compatibility
- **Patch Releases** (`v1.0.1`): Fix bugs without adding features

### Pre-release Versions

Pre-release versions are used for testing and feedback:

- **Alpha** (`v1.1.0-alpha1`): Early development, may have incomplete features
- **Beta** (`v1.1.0-beta1`): Feature-complete, undergoing testing
- **Release Candidate** (`v1.1.0-rc1`): Final testing before stable release

## Git Tagging Strategy

### Version Tags

Each release is tagged with the full version number:
```bash
git tag v1.0.0
git tag v1.1.0-beta1
```

### Moving Tags

For stable releases, we maintain moving tags for easier consumption:

- `v1` - Points to the latest v1.x.x release
- `v1.0` - Points to the latest v1.0.x release

This allows users to reference `@v1` for automatic minor updates while staying on the same major version.

## Compatibility Guarantees

### Major Version Compatibility

Within a major version (e.g., all v1.x.x releases):

- **Action Interface**: Input/output parameters remain compatible
- **Configuration Format**: YAML configuration structure is stable
- **Generated Output**: JSON structure and file locations are consistent
- **API Behavior**: Core functionality behavior is preserved

### Breaking Changes

Breaking changes that require a major version bump include:

- Removing or renaming action inputs/outputs
- Changing configuration file format
- Modifying generated file structure or naming
- Removing or significantly changing core features
- Changing minimum requirements (Python version, dependencies)

### Deprecation Policy

Before removing features in a major release:

1. Feature is marked as deprecated in documentation
2. Warning messages are added to logs when deprecated features are used
3. Deprecation notice is maintained for at least one minor version
4. Feature is removed in the next major version

## Release Process

### Automated Release Workflow

Releases are managed through GitHub Actions:

1. **Tag Creation**: Push a version tag to trigger release workflow
2. **Validation**: Automated testing and security scanning
3. **Build**: Package creation and artifact generation
4. **Release**: GitHub release creation with changelog
5. **Distribution**: Tag updates for marketplace consumption

### Manual Release Steps

For manual releases:

```bash
# 1. Update version
echo "v1.1.0" > .github/actions/tweet-generator/VERSION

# 2. Commit version update
git add .github/actions/tweet-generator/VERSION
git commit -m "Bump version to v1.1.0"

# 3. Create and push tag
git tag v1.1.0
git push origin v1.1.0

# 4. Release workflow will automatically trigger
```

### Hotfix Process

For critical bug fixes:

1. Create hotfix branch from the affected release tag
2. Apply minimal fix
3. Create patch release (increment PATCH version)
4. Follow standard release process

## Version Management

### Development Versions

During development, use pre-release versions:
- Start with `v1.1.0-alpha1` for new minor versions
- Progress through `alpha` → `beta` → `rc` → stable

### Version File

The `VERSION` file in the action directory contains the current version:
```
v1.0.0
```

This file is used by:
- Release workflows for validation
- Action metadata for version reporting
- Documentation generation

## Changelog Management

### Automated Changelog

The release workflow automatically generates changelogs from git commits:
- Commit messages should be descriptive
- Use conventional commit format when possible
- Breaking changes should be clearly marked

### Manual Changelog

For major releases, maintain a manual `CHANGELOG.md`:
```markdown
# Changelog

## [2.0.0] - 2024-01-15

### Breaking Changes
- Removed deprecated `legacy_mode` configuration option
- Changed output file naming convention

### Added
- New engagement optimization algorithms
- Support for custom hook templates

### Fixed
- Character limit validation edge cases
```

## Migration Guides

### Major Version Migrations

Each major version includes a migration guide:
- `MIGRATION_v1_to_v2.md` - Detailed upgrade instructions
- Breaking changes documentation
- Configuration update examples
- Automated migration scripts when possible

### Compatibility Matrix

| Action Version | Python | GitHub Actions | OpenRouter API |
|---------------|--------|----------------|----------------|
| v1.0.x        | 3.9+   | Any           | v1             |
| v1.1.x        | 3.9+   | Any           | v1             |
| v2.0.x        | 3.10+  | Any           | v1, v2         |

## Best Practices

### For Users

1. **Pin to Major Versions**: Use `@v1` for automatic updates within major versions
2. **Test Pre-releases**: Help validate beta versions in non-production environments
3. **Review Breaking Changes**: Read migration guides before major version updates
4. **Monitor Deprecations**: Watch for deprecation warnings in logs

### For Maintainers

1. **Semantic Versioning**: Strictly follow SemVer guidelines
2. **Comprehensive Testing**: Ensure all tests pass before releases
3. **Clear Documentation**: Update docs with every release
4. **Backward Compatibility**: Maintain compatibility within major versions
5. **Security Updates**: Prioritize security fixes with patch releases

## Support Policy

### Long-term Support (LTS)

- **Current Major Version**: Full support with features and bug fixes
- **Previous Major Version**: Security fixes and critical bug fixes for 12 months
- **Older Versions**: Community support only

### End of Life (EOL)

Versions reach EOL when:
- Two major versions behind current (e.g., v1.x when v3.x is released)
- Critical security vulnerabilities cannot be patched
- Dependencies reach EOL

EOL versions receive:
- 90-day advance notice
- Final security update if possible
- Migration documentation to supported versions

## Questions and Support

For version-related questions:
- Check the [FAQ](FAQ.md) for common version questions
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for upgrade issues
- Open an issue for version-specific problems
- Consult migration guides for major version updates