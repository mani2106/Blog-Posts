"""
Custom exceptions for the Tweet Thread Generator.

This module defines specific exception types used throughout the system
to provide better error handling and debugging information.
"""


class TweetGeneratorError(Exception):
    """Base exception for all tweet generator errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(TweetGeneratorError):
    """Raised when configuration is invalid or missing."""
    pass


class ContentDetectionError(TweetGeneratorError):
    """Raised when content detection fails."""
    pass


class StyleAnalysisError(TweetGeneratorError):
    """Raised when style analysis fails."""
    pass


class AIGenerationError(TweetGeneratorError):
    """Raised when AI content generation fails."""
    pass


class ValidationError(TweetGeneratorError):
    """Raised when content validation fails."""
    pass


class SafetyError(TweetGeneratorError):
    """Raised when content safety checks fail."""
    pass


class GitHubAPIError(TweetGeneratorError):
    """Raised when GitHub API operations fail."""
    pass


class TwitterAPIError(TweetGeneratorError):
    """Raised when Twitter API operations fail."""
    pass


class FileOperationError(TweetGeneratorError):
    """Raised when file operations fail."""
    pass


class OpenRouterAPIError(TweetGeneratorError):
    """Raised when OpenRouter API operations fail."""
    pass