"""
Twitter API integration for the Tweet Thread Generator.

This module handles Twitter API v2 authentication, thread posting functionality,
rate limiting, and error handling for the tweet generation workflow.
"""

import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import tweepy
from tweepy.errors import TweepyException, TooManyRequests, Unauthorized, Forbidden

from models import ThreadData, Tweet, PostResult, GeneratorConfig
from exceptions import TwitterAPIError
from utils import validate_twitter_character_limit


logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Rate limit information for Twitter API."""
    limit: int
    remaining: int
    reset_time: datetime


class TwitterClient:
    """
    Twitter API v2 client for posting tweet threads.

    Handles authentication, rate limiting, thread posting with proper sequencing,
    and error recovery for the Twitter API integration.
    """

    def __init__(self, config: GeneratorConfig):
        """
        Initialize Twitter client with API credentials.

        Args:
            config: GeneratorConfig with Twitter API credentials

        Raises:
            TwitterAPIError: If authentication fails
        """
        self.config = config
        self.client = None
        self.api = None
        self._rate_limit_info: Optional[RateLimitInfo] = None
        self._last_tweet_time: Optional[datetime] = None

        # Twitter API rate limits (tweets per 15-minute window)
        self.TWEET_RATE_LIMIT = 300
        self.MIN_TWEET_INTERVAL = 1.0  # Minimum seconds between tweets

        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Tweepy client with authentication."""
        try:
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                consumer_key=self.config.twitter_api_key,
                consumer_secret=self.config.twitter_api_secret,
                access_token=self.config.twitter_access_token,
                access_token_secret=self.config.twitter_access_token_secret,
                wait_on_rate_limit=True
            )

            # Also initialize v1.1 API for additional functionality if needed
            auth = tweepy.OAuth1UserHandler(
                self.config.twitter_api_key,
                self.config.twitter_api_secret,
                self.config.twitter_access_token,
                self.config.twitter_access_token_secret
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)

            # Verify credentials
            self._verify_credentials()

            logger.info("Twitter API client initialized successfully")

        except Exception as e:
            raise TwitterAPIError(f"Failed to initialize Twitter client: {str(e)}")

    def _verify_credentials(self) -> None:
        """Verify Twitter API credentials."""
        try:
            user = self.client.get_me()
            if user and user.data:
                logger.info(f"Twitter authentication successful for user: @{user.data.username}")
            else:
                raise TwitterAPIError("Failed to verify Twitter credentials")
        except Unauthorized:
            raise TwitterAPIError("Twitter API credentials are invalid")
        except Exception as e:
            raise TwitterAPIError(f"Failed to verify Twitter credentials: {str(e)}")

    def post_thread(self, thread: ThreadData) -> PostResult:
        """
        Post a complete tweet thread to Twitter.

        Args:
            thread: ThreadData containing tweets to post

        Returns:
            PostResult with posting status and tweet IDs

        Raises:
            TwitterAPIError: If posting fails
        """
        if self.config.dry_run_mode:
            logger.info("Dry run mode: Would post thread with %d tweets", len(thread.tweets))
            return PostResult(
                success=True,
                tweet_ids=[f"dry_run_{i}" for i in range(len(thread.tweets))],
                platform="twitter"
            )

        try:
            tweet_ids = []
            previous_tweet_id = None

            logger.info("Starting to post thread with %d tweets", len(thread.tweets))

            for i, tweet in enumerate(thread.tweets):
                # Validate character limit
                if not validate_twitter_character_limit(tweet.content):
                    raise TwitterAPIError(f"Tweet {i+1} exceeds character limit: {len(tweet.content)} chars")

                # Rate limiting: ensure minimum interval between tweets
                self._handle_rate_limiting()

                # Post tweet
                tweet_id = self._post_single_tweet(
                    content=tweet.content,
                    reply_to_id=previous_tweet_id,
                    position=i + 1,
                    total_tweets=len(thread.tweets)
                )

                tweet_ids.append(tweet_id)
                previous_tweet_id = tweet_id

                logger.info("Posted tweet %d/%d (ID: %s)", i + 1, len(thread.tweets), tweet_id)

                # Update last tweet time for rate limiting
                self._last_tweet_time = datetime.now()

            logger.info("Successfully posted complete thread with %d tweets", len(tweet_ids))

            return PostResult(
                success=True,
                tweet_ids=tweet_ids,
                platform="twitter",
                posted_at=datetime.now()
            )

        except TwitterAPIError:
            raise
        except Exception as e:
            raise TwitterAPIError(f"Failed to post thread: {str(e)}")

    def _post_single_tweet(
        self,
        content: str,
        reply_to_id: Optional[str] = None,
        position: int = 1,
        total_tweets: int = 1
    ) -> str:
        """
        Post a single tweet with error handling and retries.

        Args:
            content: Tweet content
            reply_to_id: ID of tweet to reply to (for threading)
            position: Position in thread (for logging)
            total_tweets: Total tweets in thread (for logging)

        Returns:
            Tweet ID of posted tweet

        Raises:
            TwitterAPIError: If posting fails after retries
        """
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                # Post tweet using Twitter API v2
                response = self.client.create_tweet(
                    text=content,
                    in_reply_to_tweet_id=reply_to_id
                )

                if response and response.data:
                    return str(response.data['id'])
                else:
                    raise TwitterAPIError("No tweet ID returned from Twitter API")

            except TooManyRequests as e:
                logger.warning("Rate limit exceeded, waiting...")
                self._handle_rate_limit_exceeded(e)
                continue

            except (Unauthorized, Forbidden) as e:
                raise TwitterAPIError(f"Twitter API authorization error: {str(e)}")

            except TweepyException as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        "Tweet posting failed (attempt %d/%d): %s. Retrying in %.1fs...",
                        attempt + 1, max_retries, str(e), retry_delay
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    raise TwitterAPIError(f"Failed to post tweet after {max_retries} attempts: {str(e)}")

            except Exception as e:
                raise TwitterAPIError(f"Unexpected error posting tweet: {str(e)}")

        raise TwitterAPIError(f"Failed to post tweet after {max_retries} attempts")

    def _handle_rate_limiting(self) -> None:
        """Handle rate limiting between tweets."""
        if self._last_tweet_time:
            time_since_last = (datetime.now() - self._last_tweet_time).total_seconds()
            if time_since_last < self.MIN_TWEET_INTERVAL:
                sleep_time = self.MIN_TWEET_INTERVAL - time_since_last
                logger.info("Rate limiting: sleeping for %.1f seconds", sleep_time)
                time.sleep(sleep_time)

    def _handle_rate_limit_exceeded(self, error: TooManyRequests) -> None:
        """Handle rate limit exceeded error."""
        # Extract reset time from error if available
        reset_time = None
        if hasattr(error, 'response') and error.response:
            headers = error.response.headers
            reset_timestamp = headers.get('x-rate-limit-reset')
            if reset_timestamp:
                reset_time = datetime.fromtimestamp(int(reset_timestamp))

        if reset_time:
            wait_time = (reset_time - datetime.now()).total_seconds()
            if wait_time > 0:
                logger.info("Rate limit exceeded. Waiting %.1f seconds until reset...", wait_time)
                time.sleep(wait_time + 1)  # Add 1 second buffer
            else:
                logger.info("Rate limit reset time has passed, continuing...")
        else:
            # Default wait time if reset time not available
            wait_time = 900  # 15 minutes
            logger.info("Rate limit exceeded. Waiting %d seconds (default)...", wait_time)
            time.sleep(wait_time)

    def get_rate_limit_status(self) -> Optional[RateLimitInfo]:
        """
        Get current rate limit status.

        Returns:
            RateLimitInfo with current rate limit status, or None if unavailable
        """
        try:
            # Use v1.1 API to get rate limit status
            rate_limit_status = self.api.get_rate_limit_status(resources=['statuses'])

            if 'statuses' in rate_limit_status['resources']:
                status_info = rate_limit_status['resources']['statuses']['/statuses/update']

                return RateLimitInfo(
                    limit=status_info['limit'],
                    remaining=status_info['remaining'],
                    reset_time=datetime.fromtimestamp(status_info['reset'])
                )
        except Exception as e:
            logger.warning("Failed to get rate limit status: %s", str(e))

        return None

    def validate_thread_for_posting(self, thread: ThreadData) -> List[str]:
        """
        Validate thread before posting.

        Args:
            thread: ThreadData to validate

        Returns:
            List of validation warnings (empty if no issues)
        """
        warnings = []

        # Check thread length
        if len(thread.tweets) > 25:
            warnings.append(f"Thread has {len(thread.tweets)} tweets (recommended max: 25)")

        # Check individual tweet character limits
        for i, tweet in enumerate(thread.tweets):
            if not validate_twitter_character_limit(tweet.content):
                warnings.append(f"Tweet {i+1} exceeds 280 character limit ({len(tweet.content)} chars)")

        # Check for empty tweets
        for i, tweet in enumerate(thread.tweets):
            if not tweet.content.strip():
                warnings.append(f"Tweet {i+1} is empty")

        # Check rate limit status
        rate_limit = self.get_rate_limit_status()
        if rate_limit and rate_limit.remaining < len(thread.tweets):
            warnings.append(
                f"Insufficient rate limit remaining: {rate_limit.remaining} < {len(thread.tweets)} tweets"
            )

        return warnings

    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet by ID.

        Args:
            tweet_id: ID of tweet to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.delete_tweet(tweet_id)
            return response.data.get('deleted', False) if response and response.data else False
        except Exception as e:
            logger.error("Failed to delete tweet %s: %s", tweet_id, str(e))
            return False

    def get_tweet_info(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a posted tweet.

        Args:
            tweet_id: ID of tweet to retrieve

        Returns:
            Tweet information dict, or None if not found
        """
        try:
            response = self.client.get_tweet(
                tweet_id,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )

            if response and response.data:
                tweet_data = response.data
                return {
                    'id': tweet_data.id,
                    'text': tweet_data.text,
                    'created_at': tweet_data.created_at.isoformat() if tweet_data.created_at else None,
                    'author_id': tweet_data.author_id,
                    'public_metrics': tweet_data.public_metrics if hasattr(tweet_data, 'public_metrics') else None
                }
        except Exception as e:
            logger.error("Failed to get tweet info for %s: %s", tweet_id, str(e))

        return None