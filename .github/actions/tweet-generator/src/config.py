"""
Configuration management and validation for the Tweet Thread Generator.

This module handles loading configuration from various sources (environment variables,
YAML files) and provides validation and default value management.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict

from models import GeneratorConfig, ValidationResult, ValidationStatus, EngagementLevel


class ConfigManager:
    """Manages configuration loading and validation."""

    DEFAULT_CONFIG_PATHS = [
        ".github/tweet-generator-config.yml",
        ".github/tweet-generator-config.yaml",
        "tweet-generator-config.yml",
        "tweet-generator-config.yaml"
    ]

    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> GeneratorConfig:
        """
        Load configuration from environment variables and optional YAML file.

        Args:
            config_path: Optional path to YAML configuration file

        Returns:
            GeneratorConfig instance with loaded settings
        """
        # Start with environment-based config
        config = GeneratorConfig.from_env()

        # Try to load YAML configuration
        yaml_config = cls._load_yaml_config(config_path)
        if yaml_config:
            config = cls._merge_yaml_config(config, yaml_config)

        return config

    @classmethod
    def _load_yaml_config(cls, config_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load configuration from YAML file."""
        paths_to_try = []

        if config_path:
            paths_to_try.append(config_path)
        else:
            paths_to_try.extend(cls.DEFAULT_CONFIG_PATHS)

        for path in paths_to_try:
            config_file = Path(path)
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except yaml.YAMLError as e:
                    # Log warning but continue with env config
                    print(f"Warning: Failed to parse YAML config {path}: {e}")
                except Exception as e:
                    print(f"Warning: Failed to load config file {path}: {e}")

        return None

    @classmethod
    def _merge_yaml_config(cls, env_config: GeneratorConfig, yaml_config: Dict[str, Any]) -> GeneratorConfig:
        """Merge YAML configuration with environment-based configuration."""
        # Environment variables take precedence over YAML
        config_dict = asdict(env_config)

        # Update with YAML values where env vars are not set
        models_config = yaml_config.get('models', {})
        if not os.getenv('OPENROUTER_MODEL') and 'planning' in models_config:
            config_dict['openrouter_model'] = models_config['planning']
        if not os.getenv('CREATIVE_MODEL') and 'creative' in models_config:
            config_dict['creative_model'] = models_config['creative']
        if not os.getenv('VERIFICATION_MODEL') and 'verification' in models_config:
            config_dict['verification_model'] = models_config['verification']

        engagement_config = yaml_config.get('engagement', {})
        if not os.getenv('ENGAGEMENT_LEVEL') and 'optimization_level' in engagement_config:
            config_dict['engagement_optimization_level'] = EngagementLevel(
                engagement_config['optimization_level']
            )
        if not os.getenv('HOOK_VARIATIONS_COUNT') and 'hook_variations' in engagement_config:
            config_dict['hook_variations_count'] = engagement_config['hook_variations']

        output_config = yaml_config.get('output', {})
        if not os.getenv('AUTO_POST_ENABLED') and 'auto_post_enabled' in output_config:
            config_dict['auto_post_enabled'] = output_config['auto_post_enabled']
        if not os.getenv('DRY_RUN') and 'dry_run_mode' in output_config:
            config_dict['dry_run_mode'] = output_config['dry_run_mode']
        if not os.getenv('MAX_TWEETS_PER_THREAD') and 'max_tweets_per_thread' in output_config:
            config_dict['max_tweets_per_thread'] = output_config['max_tweets_per_thread']

        directories_config = yaml_config.get('directories', {})
        if not os.getenv('POSTS_DIRECTORY') and 'posts' in directories_config:
            config_dict['posts_directory'] = directories_config['posts']
        if not os.getenv('NOTEBOOKS_DIRECTORY') and 'notebooks' in directories_config:
            config_dict['notebooks_directory'] = directories_config['notebooks']
        if not os.getenv('GENERATED_DIRECTORY') and 'generated' in directories_config:
            config_dict['generated_directory'] = directories_config['generated']
        if not os.getenv('POSTED_DIRECTORY') and 'posted' in directories_config:
            config_dict['posted_directory'] = directories_config['posted']

        return GeneratorConfig(**config_dict)

    @classmethod
    def create_sample_config(cls, output_path: str = ".github/tweet-generator-config.yml") -> None:
        """Create a sample configuration file."""
        sample_config = {
            'models': {
                'planning': 'google/gemini-2.5-flash-lite',
                'creative': 'google/gemini-2.5-flash-lite',
                'verification': 'google/gemini-2.5-flash-lite'
            },
            'engagement': {
                'optimization_level': 'high',
                'hook_variations': 3,
                'max_hashtags': 2
            },
            'output': {
                'auto_post_enabled': False,
                'dry_run_mode': False,
                'max_tweets_per_thread': 10
            },
            'directories': {
                'posts': '_posts',
                'notebooks': '_notebooks',
                'generated': '.generated',
                'posted': '.posted'
            },
            'style_analysis': {
                'min_posts_for_analysis': 3,
                'profile_version': '1.0.0'
            }
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)

    @classmethod
    def validate_environment(cls) -> ValidationResult:
        """Validate that the environment is properly set up."""
        errors = []
        warnings = []

        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            errors.append("Python 3.8 or higher is required")

        # Check for required directories
        required_dirs = ["_posts", "_notebooks"]
        for directory in required_dirs:
            if not Path(directory).exists():
                warnings.append(f"Directory '{directory}' does not exist - may affect style analysis")

        # Check GitHub Actions environment
        if os.getenv("GITHUB_ACTIONS"):
            if not os.getenv("GITHUB_TOKEN"):
                errors.append("GITHUB_TOKEN is required in GitHub Actions environment")
            if not os.getenv("GITHUB_REPOSITORY"):
                warnings.append("GITHUB_REPOSITORY not found - PR creation may fail")

        # Determine status
        if errors:
            status = ValidationStatus.ERROR
            message = f"Environment validation failed: {'; '.join(errors)}"
        elif warnings:
            status = ValidationStatus.WARNING
            message = f"Environment warnings: {'; '.join(warnings)}"
        else:
            status = ValidationStatus.VALID
            message = "Environment is properly configured"

        return ValidationResult(
            status=status,
            message=message,
            details={"errors": errors, "warnings": warnings}
        )