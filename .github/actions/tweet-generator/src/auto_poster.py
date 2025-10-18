"""
Auto-posting logic and controls for the Tweet Thread Generator.

This module handles auto-posting functionality including duplicate detection,
posted metadata storage, and graceful fallback to PR creation when auto-posting fails.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from models import ThreadData, BlogPost, PostResult, GeneratorConfig
from exceptions import TwitterAPIError, FileOperationError
from utils import save_json_file, ensure_directory
from twitter_client import TwitterClient


logger = logging.getLogger(__name__)


class AutoPoster:
    """
    Manages auto-posting functionality with duplicate detection and controls.

    Handles checking auto-posting flags, duplicate detection using posted metadata,
    and graceful fallback to PR creation when auto-posting fails.
    """

    def __init__(self, config: GeneratorConfig):
        """
        Initialize AutoPoster with configuration.

        Args:
            config: GeneratorConfig with auto-posting settings
        """
        self.config = config
        self.posted_directory = Path(config.posted_directory)
        self._twitter_client: Optional[TwitterClient] = None

    @property
    def twitter_client(self) -> TwitterClient:
        """Lazy-loaded Twitter client."""
        if self._twitter_client is None:
            self._twitter_client = TwitterClient(self.config)
        return self._twitter_client

    def should_auto_post(self, post: BlogPost) -> tuple[bool, str]:
        """
        Determine if a post should be auto-posted.

        Args:
            post: BlogPost to check

        Returns:
            Tuple of (should_post, reason)
        """
        # Check if auto-posting is globally enabled
        if not self.config.auto_post_enabled:
            return False, "Auto-posting is globally disabled"

        # Check if dry run mode is enabled
        if self.config.dry_run_mode:
            return False, "Running in dry-run mode"

        # Check if post has auto_post flag
        if not post.auto_post:
            return False, "Post does not have auto_post: true in frontmatter"

        # Check if post was already posted
        if self.is_already_posted(post.slug):
            return False, "Post was already posted to Twitter"

        # Check if required Twitter credentials are available
        if not self._has_twitter_credentials():
            return False, "Twitter API credentials are not configured"

        return True, "All conditions met for auto-posting"

    def is_already_posted(self, post_slug: str) -> bool:
        """
        Check if a post has already been posted to Twitter.

        Args:
            post_slug: Slug of the post to check

        Returns:
            True if already posted, False otherwise
        """
        posted_file = self.posted_directory / f"{post_slug}.json"
        return posted_file.exists()

    def get_posted_metadata(self, post_slug: str) -> Optional[Dict[str, Any]]:
        """
        Get posted metadata for a post.

        Args:
            post_slug: Slug of the post

        Returns:
            Posted metadata dict, or None if not found
        """
        posted_file = self.posted_directory / f"{post_slug}.json"

        if not posted_file.exists():
            return None

        try:
            with open(posted_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to read posted metadata for %s: %s", post_slug, str(e))
            return None

    def save_posted_metadata(self, post_slug: str, result: PostResult) -> None:
        """
        Save posted metadata to tracking file.

        Args:
            post_slug: Slug of the posted post
            result: PostResult with posting details

        Raises:
            FileOperationError: If saving fails
        """
        try:
            # Ensure posted directory exists
            ensure_directory(str(self.posted_directory))

            # Create metadata
            metadata = {
                "post_slug": post_slug,
                "success": result.success,
                "tweet_ids": result.tweet_ids,
                "platform": result.platform,
                "posted_at": result.posted_at.isoformat(),
                "error_message": result.error_message,
                "thread_length": len(result.tweet_ids) if result.tweet_ids else 0,
                "created_at": datetime.now().isoformat()
            }

            # Save to file
            posted_file = self.posted_directory / f"{post_slug}.json"
            save_json_file(metadata, str(posted_file))

            logger.info("Saved posted metadata for %s to %s", post_slug, posted_file)

        except Exception as e:
            raise FileOperationError(f"Failed to save posted metadata for {post_slug}: {str(e)}")

    def attempt_auto_post(self, thread: ThreadData, post: BlogPost) -> PostResult:
        """
        Attempt to auto-post a thread with error handling and fallback.

        Args:
            thread: ThreadData to post
            post: BlogPost being posted

        Returns:
            PostResult with posting status
        """
        # Check if auto-posting should proceed
        should_post, reason = self.should_auto_post(post)

        if not should_post:
            logger.info("Skipping auto-post for %s: %s", post.slug, reason)
            return PostResult(
                success=False,
                error_message=f"Auto-posting skipped: {reason}",
                platform="twitter"
            )

        try:
            logger.info("Attempting auto-post for %s", post.slug)

            # Post to Twitter
            result = self.twitter_client.post_thread(thread)

            # Save posted metadata if successful
            if result.success:
                self.save_posted_metadata(post.slug, result)
                logger.info("Successfully auto-posted %s with %d tweets",
                           post.slug, len(result.tweet_ids))
            else:
                logger.error("Auto-posting failed for %s: %s", post.slug, result.error_message)

            return result

        except TwitterAPIError as e:
            logger.error("Twitter API error during auto-post for %s: %s", post.slug, str(e))
            return PostResult(
                success=False,
                error_message=f"Twitter API error: {str(e)}",
                platform="twitter"
            )

        except Exception as e:
            logger.error("Unexpected error during auto-post for %s: %s", post.slug, str(e))
            return PostResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                platform="twitter"
            )

    def cleanup_failed_posts(self, post_slug: str, tweet_ids: List[str]) -> None:
        """
        Clean up partially posted threads by deleting tweets.

        Args:
            post_slug: Slug of the post
            tweet_ids: List of tweet IDs to delete
        """
        if not tweet_ids:
            return

        logger.info("Cleaning up %d tweets for failed post %s", len(tweet_ids), post_slug)

        deleted_count = 0
        for tweet_id in tweet_ids:
            try:
                if self.twitter_client.delete_tweet(tweet_id):
                    deleted_count += 1
                    logger.info("Deleted tweet %s", tweet_id)
                else:
                    logger.warning("Failed to delete tweet %s", tweet_id)
            except Exception as e:
                logger.error("Error deleting tweet %s: %s", tweet_id, str(e))

        logger.info("Cleaned up %d/%d tweets for %s", deleted_count, len(tweet_ids), post_slug)

    def get_posting_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about posted threads.

        Returns:
            Dictionary with posting statistics
        """
        if not self.posted_directory.exists():
            return {
                "total_posts": 0,
                "successful_posts": 0,
                "failed_posts": 0,
                "total_tweets": 0
            }

        stats = {
            "total_posts": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "total_tweets": 0,
            "posts_by_date": {},
            "average_thread_length": 0.0
        }

        thread_lengths = []

        try:
            for posted_file in self.posted_directory.glob("*.json"):
                try:
                    with open(posted_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    stats["total_posts"] += 1

                    if metadata.get("success", False):
                        stats["successful_posts"] += 1
                        thread_length = metadata.get("thread_length", 0)
                        stats["total_tweets"] += thread_length
                        thread_lengths.append(thread_length)
                    else:
                        stats["failed_posts"] += 1

                    # Track posts by date
                    posted_at = metadata.get("posted_at", "")
                    if posted_at:
                        date_key = posted_at[:10]  # YYYY-MM-DD
                        stats["posts_by_date"][date_key] = stats["posts_by_date"].get(date_key, 0) + 1

                except Exception as e:
                    logger.warning("Failed to process posted metadata file %s: %s", posted_file, str(e))

            # Calculate average thread length
            if thread_lengths:
                stats["average_thread_length"] = sum(thread_lengths) / len(thread_lengths)

        except Exception as e:
            logger.error("Failed to calculate posting statistics: %s", str(e))

        return stats

    def _has_twitter_credentials(self) -> bool:
        """Check if Twitter API credentials are configured."""
        return all([
            self.config.twitter_api_key,
            self.config.twitter_api_secret,
            self.config.twitter_access_token,
            self.config.twitter_access_token_secret
        ])

    def validate_auto_posting_setup(self) -> List[str]:
        """
        Validate auto-posting setup and return any issues.

        Returns:
            List of validation issues (empty if setup is valid)
        """
        issues = []

        # Check if auto-posting is enabled
        if not self.config.auto_post_enabled:
            issues.append("Auto-posting is disabled in configuration")

        # Check Twitter credentials
        if not self._has_twitter_credentials():
            missing_creds = []
            if not self.config.twitter_api_key:
                missing_creds.append("TWITTER_API_KEY")
            if not self.config.twitter_api_secret:
                missing_creds.append("TWITTER_API_SECRET")
            if not self.config.twitter_access_token:
                missing_creds.append("TWITTER_ACCESS_TOKEN")
            if not self.config.twitter_access_token_secret:
                missing_creds.append("TWITTER_ACCESS_TOKEN_SECRET")

            issues.append(f"Missing Twitter credentials: {', '.join(missing_creds)}")

        # Check posted directory
        try:
            ensure_directory(str(self.posted_directory))
        except Exception as e:
            issues.append(f"Cannot create posted directory: {str(e)}")

        # Test Twitter API connection if credentials are available
        if self._has_twitter_credentials() and not self.config.dry_run_mode:
            try:
                twitter_client = TwitterClient(self.config)
                # If we get here without exception, credentials are valid
            except TwitterAPIError as e:
                issues.append(f"Twitter API connection failed: {str(e)}")
            except Exception as e:
                issues.append(f"Unexpected error testing Twitter connection: {str(e)}")

        return issues

    def list_posted_threads(self) -> List[Dict[str, Any]]:
        """
        List all posted threads with metadata.

        Returns:
            List of posted thread metadata
        """
        threads = []

        if not self.posted_directory.exists():
            return threads

        try:
            for posted_file in sorted(self.posted_directory.glob("*.json")):
                try:
                    with open(posted_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    # Add filename for reference
                    metadata["metadata_file"] = posted_file.name
                    threads.append(metadata)

                except Exception as e:
                    logger.warning("Failed to read posted metadata file %s: %s", posted_file, str(e))

        except Exception as e:
            logger.error("Failed to list posted threads: %s", str(e))

        return threads