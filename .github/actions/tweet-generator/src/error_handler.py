"""
Error handling and recovery system for the Tweet Thread Generator.

This module provides comprehensive error handling, retry mechanisms,
and recovery strategies for various failure scenarios.
"""

import time
import logging
import traceback
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass
from enum import Enum
import random

from exceptions import (
    TweetGeneratorError, OpenRouterAPIError, ValidationError,
    SafetyError, GitHubAPIError, TwitterAPIError, ConfigurationError
)
from models import ValidationResult, ValidationStatus


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(str, Enum):
    """Recovery strategy types."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    FAIL = "fail"
    REGENERATE = "regenerate"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: str
    component: str
    input_data: Dict[str, Any]
    attempt_number: int = 1
    max_attempts: int = 3
    error_history: List[str] = None

    def __post_init__(self):
        if self.error_history is None:
            self.error_history = []


@dataclass
class RecoveryResult:
    """Result of error recovery attempt."""
    success: bool
    strategy_used: RecoveryStrategy
    result_data: Any = None
    error_message: str = ""
    attempts_made: int = 0
    recovery_time: float = 0.0


class ErrorHandler:
    """Comprehensive error handling and recovery system."""

    def __init__(self):
        """Initialize error handler."""
        self.logger = logging.getLogger(__name__)

        # Retry configuration
        self.retry_config = {
            "max_attempts": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "exponential_base": 2.0,
            "jitter": True
        }

        # Error severity mapping
        self.error_severity_map = {
            OpenRouterAPIError: ErrorSeverity.HIGH,
            ValidationError: ErrorSeverity.MEDIUM,
            SafetyError: ErrorSeverity.HIGH,
            GitHubAPIError: ErrorSeverity.MEDIUM,
            TwitterAPIError: ErrorSeverity.MEDIUM,
            ConfigurationError: ErrorSeverity.CRITICAL,
            TweetGeneratorError: ErrorSeverity.MEDIUM
        }

        # Recovery strategy mapping
        self.recovery_strategies = {
            OpenRouterAPIError: [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK],
            ValidationError: [RecoveryStrategy.REGENERATE, RecoveryStrategy.SKIP],
            SafetyError: [RecoveryStrategy.REGENERATE, RecoveryStrategy.SKIP],
            GitHubAPIError: [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP],
            TwitterAPIError: [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP],
            ConfigurationError: [RecoveryStrategy.FAIL],
            TweetGeneratorError: [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP]
        }

    def handle_error(self,
                    error: Exception,
                    context: ErrorContext,
                    recovery_callback: Optional[Callable] = None) -> RecoveryResult:
        """
        Handle error with appropriate recovery strategy.

        Args:
            error: Exception that occurred
            context: Error context information
            recovery_callback: Optional callback for custom recovery

        Returns:
            RecoveryResult with outcome of recovery attempt
        """
        start_time = time.time()

        # Log the error
        self._log_error(error, context)

        # Determine error severity
        severity = self._get_error_severity(error)

        # Get recovery strategies for this error type
        strategies = self._get_recovery_strategies(error)

        # Try recovery strategies in order
        for strategy in strategies:
            try:
                result = self._execute_recovery_strategy(
                    strategy, error, context, recovery_callback
                )

                if result.success:
                    recovery_time = time.time() - start_time
                    result.recovery_time = recovery_time

                    self.logger.info(
                        f"Error recovery successful using {strategy.value} strategy "
                        f"after {result.attempts_made} attempts in {recovery_time:.2f}s"
                    )
                    return result

            except Exception as recovery_error:
                self.logger.warning(
                    f"Recovery strategy {strategy.value} failed: {recovery_error}"
                )
                continue

        # All recovery strategies failed
        recovery_time = time.time() - start_time
        self.logger.error(
            f"All recovery strategies failed for {type(error).__name__} "
            f"in {context.operation}"
        )

        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.FAIL,
            error_message=str(error),
            attempts_made=context.attempt_number,
            recovery_time=recovery_time
        )

    def retry_with_backoff(self,
                          func: Callable,
                          *args,
                          max_attempts: int = None,
                          **kwargs) -> Any:
        """
        Retry function with exponential backoff.

        Args:
            func: Function to retry
            *args: Function arguments
            max_attempts: Maximum retry attempts
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        max_attempts = max_attempts or self.retry_config["max_attempts"]
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt == max_attempts:
                    # Last attempt, don't wait
                    break

                # Calculate delay with exponential backoff and jitter
                delay = self._calculate_backoff_delay(attempt)

                self.logger.warning(
                    f"Attempt {attempt}/{max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )

                time.sleep(delay)

        # All attempts failed
        self.logger.error(
            f"Function {func.__name__} failed after {max_attempts} attempts"
        )
        raise last_exception

    def handle_openrouter_api_error(self,
                                   error: OpenRouterAPIError,
                                   context: ErrorContext) -> RecoveryResult:
        """
        Handle OpenRouter API specific errors.

        Args:
            error: OpenRouter API error
            context: Error context

        Returns:
            Recovery result
        """
        error_message = str(error)

        # Check for specific error types
        if "rate limit" in error_message.lower():
            return self._handle_rate_limit_error(error, context)
        elif "authentication" in error_message.lower():
            return self._handle_auth_error(error, context)
        elif "model not found" in error_message.lower():
            return self._handle_model_error(error, context)
        elif "timeout" in error_message.lower():
            return self._handle_timeout_error(error, context)
        else:
            # Generic API error - try retry with backoff
            return self._retry_with_exponential_backoff(error, context)

    def handle_validation_error(self,
                               error: ValidationError,
                               context: ErrorContext,
                               regenerate_callback: Optional[Callable] = None) -> RecoveryResult:
        """
        Handle content validation errors.

        Args:
            error: Validation error
            context: Error context
            regenerate_callback: Callback to regenerate content

        Returns:
            Recovery result
        """
        if regenerate_callback and context.attempt_number < context.max_attempts:
            try:
                # Try to regenerate content with stricter parameters
                self.logger.info("Attempting content regeneration with stricter parameters")

                # Modify generation parameters to be more conservative
                modified_context = self._create_conservative_context(context)
                result = regenerate_callback(modified_context)

                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.REGENERATE,
                    result_data=result,
                    attempts_made=context.attempt_number + 1
                )

            except Exception as regen_error:
                self.logger.warning(f"Content regeneration failed: {regen_error}")

        # If regeneration fails or not available, skip this content
        return RecoveryResult(
            success=True,  # Skipping is considered successful recovery
            strategy_used=RecoveryStrategy.SKIP,
            error_message=f"Skipped due to validation error: {error}",
            attempts_made=context.attempt_number
        )

    def handle_safety_error(self,
                           error: SafetyError,
                           context: ErrorContext) -> RecoveryResult:
        """
        Handle content safety errors.

        Args:
            error: Safety error
            context: Error context

        Returns:
            Recovery result
        """
        # Safety errors are serious - we should skip rather than retry
        self.logger.warning(
            f"Content safety violation in {context.operation}: {error}"
        )

        return RecoveryResult(
            success=True,  # Skipping unsafe content is successful
            strategy_used=RecoveryStrategy.SKIP,
            error_message=f"Skipped due to safety violation: {error}",
            attempts_made=context.attempt_number
        )

    def create_fallback_content(self, context: ErrorContext) -> Dict[str, Any]:
        """
        Create fallback content when AI generation fails.

        Args:
            context: Error context with original input

        Returns:
            Fallback content dictionary
        """
        # Extract basic information from context
        post_data = context.input_data.get("post", {})
        title = post_data.get("title", "Blog Post")

        # Create simple fallback thread
        fallback_tweets = [
            f"📝 New blog post: {title}",
            f"Check it out here: {post_data.get('canonical_url', '[URL]')}",
            "What are your thoughts? Let me know in the comments! 💭"
        ]

        return {
            "tweets": fallback_tweets,
            "hook_variations": [fallback_tweets[0]],
            "hashtags": ["#blog", "#content"],
            "engagement_score": 0.5,
            "fallback_used": True
        }

    def _log_error(self, error: Exception, context: ErrorContext):
        """Log error with context information."""
        self.logger.error(
            f"Error in {context.operation} (attempt {context.attempt_number}): "
            f"{type(error).__name__}: {error}",
            extra={
                "operation": context.operation,
                "component": context.component,
                "attempt": context.attempt_number,
                "max_attempts": context.max_attempts,
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc()
            }
        )

    def _get_error_severity(self, error: Exception) -> ErrorSeverity:
        """Get error severity level."""
        error_type = type(error)
        return self.error_severity_map.get(error_type, ErrorSeverity.MEDIUM)

    def _get_recovery_strategies(self, error: Exception) -> List[RecoveryStrategy]:
        """Get recovery strategies for error type."""
        error_type = type(error)
        return self.recovery_strategies.get(error_type, [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP])

    def _execute_recovery_strategy(self,
                                  strategy: RecoveryStrategy,
                                  error: Exception,
                                  context: ErrorContext,
                                  recovery_callback: Optional[Callable]) -> RecoveryResult:
        """Execute specific recovery strategy."""
        if strategy == RecoveryStrategy.RETRY:
            return self._retry_with_exponential_backoff(error, context)
        elif strategy == RecoveryStrategy.FALLBACK:
            return self._use_fallback_content(error, context)
        elif strategy == RecoveryStrategy.SKIP:
            return self._skip_operation(error, context)
        elif strategy == RecoveryStrategy.REGENERATE and recovery_callback:
            return self._regenerate_content(error, context, recovery_callback)
        elif strategy == RecoveryStrategy.FAIL:
            return RecoveryResult(
                success=False,
                strategy_used=strategy,
                error_message=str(error)
            )
        else:
            raise ValueError(f"Unknown recovery strategy: {strategy}")

    def _retry_with_exponential_backoff(self,
                                       error: Exception,
                                       context: ErrorContext) -> RecoveryResult:
        """Implement retry with exponential backoff."""
        if context.attempt_number >= context.max_attempts:
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.RETRY,
                error_message=f"Max retry attempts ({context.max_attempts}) exceeded",
                attempts_made=context.attempt_number
            )

        # Calculate delay
        delay = self._calculate_backoff_delay(context.attempt_number)

        self.logger.info(
            f"Retrying {context.operation} in {delay:.2f}s "
            f"(attempt {context.attempt_number + 1}/{context.max_attempts})"
        )

        time.sleep(delay)

        # Return success to indicate retry should be attempted
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.RETRY,
            attempts_made=context.attempt_number + 1
        )

    def _use_fallback_content(self,
                             error: Exception,
                             context: ErrorContext) -> RecoveryResult:
        """Use fallback content generation."""
        try:
            fallback_content = self.create_fallback_content(context)

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.FALLBACK,
                result_data=fallback_content,
                attempts_made=context.attempt_number
            )

        except Exception as fallback_error:
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.FALLBACK,
                error_message=f"Fallback generation failed: {fallback_error}",
                attempts_made=context.attempt_number
            )

    def _skip_operation(self,
                       error: Exception,
                       context: ErrorContext) -> RecoveryResult:
        """Skip the current operation."""
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.SKIP,
            error_message=f"Operation skipped due to: {error}",
            attempts_made=context.attempt_number
        )

    def _regenerate_content(self,
                           error: Exception,
                           context: ErrorContext,
                           regenerate_callback: Callable) -> RecoveryResult:
        """Regenerate content with modified parameters."""
        try:
            modified_context = self._create_conservative_context(context)
            result = regenerate_callback(modified_context)

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.REGENERATE,
                result_data=result,
                attempts_made=context.attempt_number + 1
            )

        except Exception as regen_error:
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.REGENERATE,
                error_message=f"Regeneration failed: {regen_error}",
                attempts_made=context.attempt_number + 1
            )

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        base_delay = self.retry_config["base_delay"]
        exponential_base = self.retry_config["exponential_base"]
        max_delay = self.retry_config["max_delay"]

        # Exponential backoff
        delay = base_delay * (exponential_base ** (attempt - 1))

        # Cap at max delay
        delay = min(delay, max_delay)

        # Add jitter if enabled
        if self.retry_config["jitter"]:
            jitter = delay * 0.1 * random.random()
            delay += jitter

        return delay

    def _create_conservative_context(self, context: ErrorContext) -> ErrorContext:
        """Create more conservative context for regeneration."""
        # Create a copy with more conservative parameters
        conservative_context = ErrorContext(
            operation=context.operation,
            component=context.component,
            input_data=context.input_data.copy(),
            attempt_number=context.attempt_number + 1,
            max_attempts=context.max_attempts,
            error_history=context.error_history.copy()
        )

        # Modify parameters to be more conservative
        if "generation_params" in conservative_context.input_data:
            params = conservative_context.input_data["generation_params"]
            params["engagement_level"] = "low"
            params["max_tweets"] = min(params.get("max_tweets", 5), 5)
            params["hook_variations"] = 1

        return conservative_context

    def _handle_rate_limit_error(self,
                                error: OpenRouterAPIError,
                                context: ErrorContext) -> RecoveryResult:
        """Handle rate limit specific errors."""
        # Extract wait time from error message if available
        wait_time = 60  # Default wait time

        error_msg = str(error).lower()
        if "retry after" in error_msg:
            try:
                # Try to extract wait time from error message
                import re
                match = re.search(r'retry after (\d+)', error_msg)
                if match:
                    wait_time = int(match.group(1))
            except:
                pass

        self.logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
        time.sleep(wait_time)

        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.RETRY,
            attempts_made=context.attempt_number + 1
        )

    def _handle_auth_error(self,
                          error: OpenRouterAPIError,
                          context: ErrorContext) -> RecoveryResult:
        """Handle authentication errors."""
        # Authentication errors are usually not recoverable
        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.FAIL,
            error_message="Authentication failed - check API credentials",
            attempts_made=context.attempt_number
        )

    def _handle_model_error(self,
                           error: OpenRouterAPIError,
                           context: ErrorContext) -> RecoveryResult:
        """Handle model not found errors."""
        # Try fallback to default model
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.FALLBACK,
            error_message="Model not found - using fallback",
            attempts_made=context.attempt_number
        )

    def _handle_timeout_error(self,
                             error: OpenRouterAPIError,
                             context: ErrorContext) -> RecoveryResult:
        """Handle timeout errors."""
        # Timeout errors can be retried
        return self._retry_with_exponential_backoff(error, context)