"""
GitHub Tweet Thread Generator

AI-powered tweet thread generator for GitHub Actions that analyzes blog posts
and creates engaging social media content with style analysis and engagement optimization.
"""

__version__ = "1.0.0"
__author__ = "Blog Author"

# Import main components for easy access
from .models import (
    BlogPost,
    StyleProfile,
    ThreadData,
    Tweet,
    GeneratorConfig,
    EngagementLevel,
    HookType,
    ValidationStatus
)

from .config import ConfigManager
from .logger import setup_logging, get_logger
from .metrics import setup_metrics_collection
from .monitoring import setup_monitoring

__all__ = [
    "BlogPost",
    "StyleProfile",
    "ThreadData",
    "Tweet",
    "GeneratorConfig",
    "EngagementLevel",
    "HookType",
    "ValidationStatus",
    "ConfigManager",
    "setup_logging",
    "get_logger",
    "setup_metrics_collection",
    "setup_monitoring",
]