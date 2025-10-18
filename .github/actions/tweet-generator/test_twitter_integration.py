"""
Twitter integration tests for the Tweet Thread Generator.

This module tests Twitter API v2 integration, thread posting functionality,
duplicate detection, error handling, and rate limiting as specified in
requirements 4.1, 4.2, and 4.3.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from twitter_client import TwitterClient, RateLimitInfo
from models import (
    ThreadData, Tweet, PostResult, GeneratorConfig,
    HookType, ThreadPlan
)
from exceptions import TwitterAPIError
import tweepy
from tweepy.errors import TweepyException, TooManyRequests, Unauthorized, Forbidden


class TestTwitterClient:
    """Test suite for TwitterClient class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.config = GeneratorConfig(
            twitter_api_key="test_api_key",
            twitter_api_secret="test_api_secret",
            twitter_access_token="test_access_token",
            twitter_access_token_secret="test_access_token_secret",
            dry_run_mode=False
        )

        # Sample thread data for testing
        self.sample_thread = ThreadData(
            post_slug="test-post",
            tweets=[
                Tweet(
                    content="🚀 Want to build better APIs? Here's what most developers get wrong... (1/3)",
                    position=1,
                    hook_type=HookType.CURIOSITY
                ),
                Tweet(
                    content="The biggest mistake: Not thinking about your API consumers first. Always design your interface before implementation. (2/3)",
                    position=2
                ),
                Tweet(
                    content="Pro tip: Start with documentation, then build. Your future self (and users) will thank you! 💡 What's your API design process? (3/3)",
                    position=3
                )
            ],
            hashtags=["API", "development"],
            model_used="anthropic/claude-3-sonnet",
            generated_at=datetime.now()
        )

    @patch('twitter_client.tweepy.Client')
    @patch('twitter_client.tweepy.API')
    @patch('twitter_client.tweepy.OAuth1UserHandler')
    def test_twitter_client_initialization_success(self, mock_oauth, mock_api, mock_client):
        """Test successful Twitter client initialization."""
        # Mock successful authentication
        mock_user_data = Mock()
        mock_user_data.username = "testuser"
        mock_user = Mock()
        mock_user.data = mock_user_data

        mock_client_instance = Mock()
        mock_client_instance.get_me.return_value = mock_user
        mock_client.return_value = mock_client_instance

        client = TwitterClient(self.config)

        assert client.client == mock_client_instance
        assert client.config == self.config
        mock_client.assert_called_once()
        mock_client_instance.get_me.assert_called_once()

    @patch('twitter_client.tweepy.Client')
    def test_twitter_client_initialization_auth_failure(self, mock_client):
        """Test Twitter client initialization with authentication failure."""
        mock_client_instance = Mock()

        # Create a proper mock response for Unauthorized exception
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_response.reason = "Unauthorized"
        mock_response.json.return_value = {"errors": [{"message": "Invalid credentials"}]}

        mock_client_instance.get_me.side_effect = Unauthorized(mock_response)
        mock_client.return_value = mock_client_instance

        with pytest.raises(TwitterAPIError) as exc_info:
            TwitterClient(self.config)

        assert "Twitter API credentials are invalid" in str(exc_info.value)

    @patch('twitter_client.tweepy.Client')
    def test_twitter_client_initialization_connection_failure(self, mock_client):
        """Test Twitter client initialization with connection failure."""
        mock_client.side_effect = Exception("Connection failed")

        with pytest.raises(TwitterAPIError) as exc_info:
            TwitterClient(self.config)

        assert "Failed to initialize Twitter client" in str(exc_info.value)


class TestThreadPosting:
    """Test thread posting sequence and reply chain creation (Requirement 4.1, 4.2)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GeneratorConfig(
            twitter_api_key="test_api_key",
            twitter_api_secret="test_api_secret",
            twitter_access_token="test_access_token",
            twitter_access_token_secret="test_access_token_secret",
            dry_run_mode=False
        )

        self.sample_thread = ThreadData(
            post_slug="test-post",
            tweets=[
                Tweet(content="First tweet in thread (1/3)", position=1),
                Tweet(content="Second tweet in thread (2/3)", position=2),
                Tweet(content="Final tweet in thread (3/3)", position=3)
            ]
        )

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_thread_success(self, mock_validate, mock_init):
        """Test successful thread posting with proper reply chain."""
        mock_validate.return_value = True

        # Mock successful tweet posting
        mock_client = Mock()
        mock_responses = [
            Mock(data={'id': '123456789'}),
            Mock(data={'id': '123456790'}),
            Mock(data={'id': '123456791'})
        ]
        mock_client.create_tweet.side_effect = mock_responses

        client = TwitterClient(self.config)
        client.client = mock_client

        result = client.post_thread(self.sample_thread)

        # Verify successful result
        assert result.success is True
        assert len(result.tweet_ids) == 3
        assert result.tweet_ids == ['123456789', '123456790', '123456791']
        assert result.platform == "twitter"

        # Verify proper reply chain creation
        calls = mock_client.create_tweet.call_args_list

        # First tweet should not have reply_to
        assert calls[0][1]['text'] == "First tweet in thread (1/3)"
        assert calls[0][1]['in_reply_to_tweet_id'] is None

        # Second tweet should reply to first
        assert calls[1][1]['text'] == "Second tweet in thread (2/3)"
        assert calls[1][1]['in_reply_to_tweet_id'] == '123456789'

        # Third tweet should reply to second
        assert calls[2][1]['text'] == "Final tweet in thread (3/3)"
        assert calls[2][1]['in_reply_to_tweet_id'] == '123456790'

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_post_thread_dry_run_mode(self, mock_init):
        """Test thread posting in dry run mode."""
        config = GeneratorConfig(dry_run_mode=True)
        client = TwitterClient(config)

        result = client.post_thread(self.sample_thread)

        assert result.success is True
        assert len(result.tweet_ids) == 3
        assert all(tweet_id.startswith("dry_run_") for tweet_id in result.tweet_ids)
        assert result.platform == "twitter"

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_thread_character_limit_validation(self, mock_validate, mock_init):
        """Test character limit validation during thread posting."""
        # First tweet passes, second fails validation
        mock_validate.side_effect = [True, False, True]

        client = TwitterClient(self.config)
        # Mock the client attribute since _initialize_client is mocked
        mock_client = Mock()
        # Configure the mock to return proper response structure
        mock_response = Mock()
        mock_response.data = {'id': '123456789'}
        mock_client.create_tweet.return_value = mock_response
        client.client = mock_client

        with pytest.raises(TwitterAPIError) as exc_info:
            client.post_thread(self.sample_thread)

        assert "exceeds character limit" in str(exc_info.value)

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_thread_partial_failure_recovery(self, mock_validate, mock_init):
        """Test handling of partial thread posting failures."""
        mock_validate.return_value = True

        mock_client = Mock()
        # First tweet succeeds, second tweet fails consistently
        call_count = 0
        def side_effect_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                response = Mock()
                response.data = {'id': '123456789'}
                return response
            else:
                raise TweepyException("API error")

        mock_client.create_tweet.side_effect = side_effect_func

        client = TwitterClient(self.config)
        client.client = mock_client

        with pytest.raises(TwitterAPIError) as exc_info:
            client.post_thread(self.sample_thread)

        assert "Failed to post tweet after 3 attempts" in str(exc_info.value)

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    @patch('twitter_client.time.sleep')
    def test_post_thread_rate_limiting(self, mock_sleep, mock_validate, mock_init):
        """Test rate limiting between tweets."""
        mock_validate.return_value = True

        mock_client = Mock()
        mock_client.create_tweet.side_effect = [
            Mock(data={'id': '123456789'}),
            Mock(data={'id': '123456790'}),
            Mock(data={'id': '123456791'})
        ]

        client = TwitterClient(self.config)
        client.client = mock_client
        client._last_tweet_time = datetime.now() - timedelta(seconds=0.5)  # Recent tweet

        client.post_thread(self.sample_thread)

        # Should have slept to respect rate limiting
        mock_sleep.assert_called()
        sleep_time = mock_sleep.call_args[0][0]
        assert sleep_time > 0

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_single_tweet_retry_logic(self, mock_validate, mock_init):
        """Test retry logic for individual tweet posting."""
        mock_validate.return_value = True

        mock_client = Mock()
        # First attempt fails, second succeeds
        mock_client.create_tweet.side_effect = [
            TweepyException("Temporary error"),
            Mock(data={'id': '123456789'})
        ]

        client = TwitterClient(self.config)
        client.client = mock_client

        with patch('twitter_client.time.sleep'):
            tweet_id = client._post_single_tweet("Test tweet content")

        assert tweet_id == '123456789'
        assert mock_client.create_tweet.call_count == 2

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_single_tweet_max_retries_exceeded(self, mock_validate, mock_init):
        """Test max retries exceeded for single tweet posting."""
        mock_validate.return_value = True

        mock_client = Mock()
        mock_client.create_tweet.side_effect = TweepyException("Persistent error")

        client = TwitterClient(self.config)
        client.client = mock_client

        with patch('twitter_client.time.sleep'):
            with pytest.raises(TwitterAPIError) as exc_info:
                client._post_single_tweet("Test tweet content")

        assert "Failed to post tweet after 3 attempts" in str(exc_info.value)

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_single_tweet_authorization_error(self, mock_validate, mock_init):
        """Test handling of authorization errors (no retry)."""
        mock_validate.return_value = True

        # Create proper mock response for Unauthorized exception
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid token"
        mock_response.reason = "Unauthorized"
        mock_response.json.return_value = {"errors": [{"message": "Invalid token"}]}

        mock_client = Mock()
        mock_client.create_tweet.side_effect = Unauthorized(mock_response)

        client = TwitterClient(self.config)
        client.client = mock_client

        with pytest.raises(TwitterAPIError) as exc_info:
            client._post_single_tweet("Test tweet content")

        assert "Twitter API authorization error" in str(exc_info.value)
        # Should not retry authorization errors
        assert mock_client.create_tweet.call_count == 1


class TestRateLimitHandling:
    """Test rate limiting and API error handling (Requirement 4.2)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GeneratorConfig(
            twitter_api_key="test_api_key",
            twitter_api_secret="test_api_secret",
            twitter_access_token="test_access_token",
            twitter_access_token_secret="test_access_token_secret"
        )

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.time.sleep')
    def test_handle_rate_limit_exceeded_with_reset_time(self, mock_sleep, mock_init):
        """Test handling rate limit exceeded with reset time in headers."""
        client = TwitterClient(self.config)

        # Mock rate limit error with reset time
        reset_timestamp = int((datetime.now() + timedelta(minutes=15)).timestamp())

        # Create proper mock response for TooManyRequests exception
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {'x-rate-limit-reset': str(reset_timestamp)}
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}

        mock_error = TooManyRequests(mock_response)
        mock_error.response = mock_response

        client._handle_rate_limit_exceeded(mock_error)

        # Should sleep until reset time + buffer
        mock_sleep.assert_called_once()
        sleep_time = mock_sleep.call_args[0][0]
        assert sleep_time > 0

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.time.sleep')
    def test_handle_rate_limit_exceeded_without_reset_time(self, mock_sleep, mock_init):
        """Test handling rate limit exceeded without reset time."""
        client = TwitterClient(self.config)

        # Create proper mock response for TooManyRequests exception
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {}
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}

        mock_error = TooManyRequests(mock_response)
        mock_error.response = mock_response

        client._handle_rate_limit_exceeded(mock_error)

        # Should sleep for default time (15 minutes)
        mock_sleep.assert_called_once_with(900)

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_get_rate_limit_status_success(self, mock_init):
        """Test successful rate limit status retrieval."""
        mock_api = Mock()
        mock_api.get_rate_limit_status.return_value = {
            'resources': {
                'statuses': {
                    '/statuses/update': {
                        'limit': 300,
                        'remaining': 250,
                        'reset': int((datetime.now() + timedelta(minutes=10)).timestamp())
                    }
                }
            }
        }

        client = TwitterClient(self.config)
        client.api = mock_api

        rate_limit = client.get_rate_limit_status()

        assert isinstance(rate_limit, RateLimitInfo)
        assert rate_limit.limit == 300
        assert rate_limit.remaining == 250
        assert isinstance(rate_limit.reset_time, datetime)

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_get_rate_limit_status_failure(self, mock_init):
        """Test rate limit status retrieval failure."""
        mock_api = Mock()
        mock_api.get_rate_limit_status.side_effect = Exception("API error")

        client = TwitterClient(self.config)
        client.api = mock_api

        rate_limit = client.get_rate_limit_status()

        assert rate_limit is None

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    @patch('twitter_client.time.sleep')
    def test_post_thread_with_rate_limit_recovery(self, mock_sleep, mock_validate, mock_init):
        """Test thread posting with rate limit recovery."""
        mock_validate.return_value = True

        # Create proper mock response for TooManyRequests exception
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {'x-rate-limit-reset': str(int(time.time()) + 60)}
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}

        rate_limit_error = TooManyRequests(mock_response)
        rate_limit_error.response = mock_response

        mock_client = Mock()
        # First tweet succeeds, second hits rate limit, third succeeds after recovery
        mock_client.create_tweet.side_effect = [
            Mock(data={'id': '123456789'}),
            rate_limit_error,
            Mock(data={'id': '123456790'}),
            Mock(data={'id': '123456791'})
        ]

        client = TwitterClient(self.config)
        client.client = mock_client

        thread_data = ThreadData(
            post_slug="test",
            tweets=[
                Tweet(content="Tweet 1", position=1),
                Tweet(content="Tweet 2", position=2),
                Tweet(content="Tweet 3", position=3)
            ]
        )

        result = client.post_thread(thread_data)

        assert result.success is True
        assert len(result.tweet_ids) == 3
        # Should have slept for rate limit recovery
        mock_sleep.assert_called()


class TestDuplicateDetection:
    """Test duplicate detection and prevention logic (Requirement 4.3)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GeneratorConfig(
            twitter_api_key="test_api_key",
            twitter_api_secret="test_api_secret",
            twitter_access_token="test_access_token",
            twitter_access_token_secret="test_access_token_secret"
        )

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_validate_thread_for_posting_character_limits(self, mock_init):
        """Test thread validation for character limits."""
        client = TwitterClient(self.config)

        # Thread with one tweet exceeding character limit
        thread_with_long_tweet = ThreadData(
            post_slug="test",
            tweets=[
                Tweet(content="Short tweet", position=1),
                Tweet(content="A" * 300, position=2),  # Exceeds 280 chars
                Tweet(content="Another short tweet", position=3)
            ]
        )

        warnings = client.validate_thread_for_posting(thread_with_long_tweet)

        assert len(warnings) > 0
        assert any("exceeds 280 character limit" in warning for warning in warnings)

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_validate_thread_for_posting_empty_tweets(self, mock_init):
        """Test thread validation for empty tweets."""
        client = TwitterClient(self.config)

        thread_with_empty_tweet = ThreadData(
            post_slug="test",
            tweets=[
                Tweet(content="Valid tweet", position=1),
                Tweet(content="", position=2),  # Empty tweet
                Tweet(content="Another valid tweet", position=3)
            ]
        )

        warnings = client.validate_thread_for_posting(thread_with_empty_tweet)

        assert len(warnings) > 0
        assert any("is empty" in warning for warning in warnings)

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_validate_thread_for_posting_too_many_tweets(self, mock_init):
        """Test thread validation for excessive tweet count."""
        client = TwitterClient(self.config)

        # Create thread with too many tweets
        long_thread = ThreadData(
            post_slug="test",
            tweets=[Tweet(content=f"Tweet {i}", position=i) for i in range(1, 30)]  # 29 tweets
        )

        warnings = client.validate_thread_for_posting(long_thread)

        assert len(warnings) > 0
        assert any("recommended max: 25" in warning for warning in warnings)

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_validate_thread_for_posting_insufficient_rate_limit(self, mock_init):
        """Test thread validation with insufficient rate limit."""
        mock_api = Mock()
        mock_api.get_rate_limit_status.return_value = {
            'resources': {
                'statuses': {
                    '/statuses/update': {
                        'limit': 300,
                        'remaining': 2,  # Only 2 remaining, but thread has 3 tweets
                        'reset': int(time.time() + 900)
                    }
                }
            }
        }

        client = TwitterClient(self.config)
        client.api = mock_api

        thread = ThreadData(
            post_slug="test",
            tweets=[
                Tweet(content="Tweet 1", position=1),
                Tweet(content="Tweet 2", position=2),
                Tweet(content="Tweet 3", position=3)
            ]
        )

        warnings = client.validate_thread_for_posting(thread)

        assert len(warnings) > 0
        assert any("Insufficient rate limit remaining" in warning for warning in warnings)

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_validate_thread_for_posting_valid_thread(self, mock_init):
        """Test thread validation with valid thread."""
        client = TwitterClient(self.config)

        valid_thread = ThreadData(
            post_slug="test",
            tweets=[
                Tweet(content="Valid tweet 1", position=1),
                Tweet(content="Valid tweet 2", position=2),
                Tweet(content="Valid tweet 3", position=3)
            ]
        )

        warnings = client.validate_thread_for_posting(valid_thread)

        assert len(warnings) == 0


class TestTwitterUtilityFunctions:
    """Test Twitter utility functions and additional features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GeneratorConfig(
            twitter_api_key="test_api_key",
            twitter_api_secret="test_api_secret",
            twitter_access_token="test_access_token",
            twitter_access_token_secret="test_access_token_secret"
        )

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_delete_tweet_success(self, mock_init):
        """Test successful tweet deletion."""
        mock_client = Mock()
        mock_client.delete_tweet.return_value = Mock(data={'deleted': True})

        client = TwitterClient(self.config)
        client.client = mock_client

        result = client.delete_tweet("123456789")

        assert result is True
        mock_client.delete_tweet.assert_called_once_with("123456789")

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_delete_tweet_failure(self, mock_init):
        """Test tweet deletion failure."""
        mock_client = Mock()
        mock_client.delete_tweet.side_effect = Exception("Delete failed")

        client = TwitterClient(self.config)
        client.client = mock_client

        result = client.delete_tweet("123456789")

        assert result is False

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_get_tweet_info_success(self, mock_init):
        """Test successful tweet info retrieval."""
        mock_tweet_data = Mock()
        mock_tweet_data.id = "123456789"
        mock_tweet_data.text = "Test tweet content"
        mock_tweet_data.created_at = datetime.now()
        mock_tweet_data.author_id = "987654321"
        mock_tweet_data.public_metrics = {"retweet_count": 5, "like_count": 10}

        mock_response = Mock()
        mock_response.data = mock_tweet_data

        mock_client = Mock()
        mock_client.get_tweet.return_value = mock_response

        client = TwitterClient(self.config)
        client.client = mock_client

        tweet_info = client.get_tweet_info("123456789")

        assert tweet_info is not None
        assert tweet_info['id'] == "123456789"
        assert tweet_info['text'] == "Test tweet content"
        assert tweet_info['author_id'] == "987654321"
        assert tweet_info['public_metrics'] == {"retweet_count": 5, "like_count": 10}

    @patch('twitter_client.TwitterClient._initialize_client')
    def test_get_tweet_info_not_found(self, mock_init):
        """Test tweet info retrieval for non-existent tweet."""
        mock_client = Mock()
        mock_client.get_tweet.side_effect = Exception("Tweet not found")

        client = TwitterClient(self.config)
        client.client = mock_client

        tweet_info = client.get_tweet_info("123456789")

        assert tweet_info is None


class TestTwitterAPIErrorScenarios:
    """Test various Twitter API error scenarios and recovery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GeneratorConfig(
            twitter_api_key="test_api_key",
            twitter_api_secret="test_api_secret",
            twitter_access_token="test_access_token",
            twitter_access_token_secret="test_access_token_secret"
        )

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_thread_forbidden_error(self, mock_validate, mock_init):
        """Test handling of forbidden errors during thread posting."""
        mock_validate.return_value = True

        # Create proper mock response for Forbidden exception
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Account suspended"
        mock_response.reason = "Forbidden"
        mock_response.json.return_value = {"errors": [{"message": "Account suspended"}]}

        mock_client = Mock()
        mock_client.create_tweet.side_effect = Forbidden(mock_response)

        client = TwitterClient(self.config)
        client.client = mock_client

        thread = ThreadData(
            post_slug="test",
            tweets=[Tweet(content="Test tweet", position=1)]
        )

        with pytest.raises(TwitterAPIError) as exc_info:
            client.post_thread(thread)

        assert "Twitter API authorization error" in str(exc_info.value)

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_thread_no_response_data(self, mock_validate, mock_init):
        """Test handling of API responses without data."""
        mock_validate.return_value = True

        mock_client = Mock()
        mock_client.create_tweet.return_value = None  # No response data

        client = TwitterClient(self.config)
        client.client = mock_client

        thread = ThreadData(
            post_slug="test",
            tweets=[Tweet(content="Test tweet", position=1)]
        )

        with pytest.raises(TwitterAPIError) as exc_info:
            client.post_thread(thread)

        assert "No tweet ID returned from Twitter API" in str(exc_info.value)

    @patch('twitter_client.TwitterClient._initialize_client')
    @patch('twitter_client.validate_twitter_character_limit')
    def test_post_thread_malformed_response(self, mock_validate, mock_init):
        """Test handling of malformed API responses."""
        mock_validate.return_value = True

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = {}  # Missing 'id' field
        mock_client.create_tweet.return_value = mock_response

        client = TwitterClient(self.config)
        client.client = mock_client

        thread = ThreadData(
            post_slug="test",
            tweets=[Tweet(content="Test tweet", position=1)]
        )

        with pytest.raises(TwitterAPIError):
            client.post_thread(thread)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])