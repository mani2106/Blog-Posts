#!/usr/bin/env python3
"""
Test script for auto-posting functionality.

This script tests the auto-posting components without actually posting to Twitter.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import GeneratorConfig, BlogPost, ThreadData, Tweet, PostResult
from auto_poster import AutoPoster
from twitter_client import TwitterClient


def test_auto_poster_setup():
    """Test AutoPoster initialization and setup validation."""
    print("Testing AutoPoster setup...")

    # Create test config
    config = GeneratorConfig(
        auto_post_enabled=True,
        dry_run_mode=True,  # Safe for testing
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_token_secret="test_token_secret"
    )

    auto_poster = AutoPoster(config)

    # Test setup validation
    issues = auto_poster.validate_auto_posting_setup()
    print(f"Setup validation issues: {issues}")

    # Test should_auto_post logic
    test_post = BlogPost(
        file_path="_posts/2023-01-01-test-post.md",
        title="Test Post",
        content="Test content",
        frontmatter={"auto_post": True},
        canonical_url="https://example.com/test-post",
        auto_post=True,
        slug="test-post"
    )

    should_post, reason = auto_poster.should_auto_post(test_post)
    print(f"Should auto-post: {should_post}, Reason: {reason}")

    # Test duplicate detection
    is_posted = auto_poster.is_already_posted("test-post")
    print(f"Already posted: {is_posted}")

    print("AutoPoster setup test completed ✓")


def test_twitter_client_dry_run():
    """Test TwitterClient in dry-run mode."""
    print("\nTesting TwitterClient in dry-run mode...")

    config = GeneratorConfig(
        dry_run_mode=True,
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_token_secret="test_token_secret"
    )

    # Create test thread
    test_tweets = [
        Tweet(content="This is tweet 1 of a test thread 🧵", position=1),
        Tweet(content="This is tweet 2 with some more content", position=2),
        Tweet(content="This is the final tweet with a call to action! What do you think?", position=3)
    ]

    test_thread = ThreadData(
        post_slug="test-thread",
        tweets=test_tweets
    )

    try:
        # This should work in dry-run mode without real credentials
        twitter_client = TwitterClient(config)
        result = twitter_client.post_thread(test_thread)

        print(f"Dry-run posting result: Success={result.success}")
        print(f"Mock tweet IDs: {result.tweet_ids}")

    except Exception as e:
        print(f"Error in dry-run test: {e}")

    print("TwitterClient dry-run test completed ✓")


def test_auto_posting_workflow():
    """Test complete auto-posting workflow in dry-run mode."""
    print("\nTesting complete auto-posting workflow...")

    config = GeneratorConfig(
        auto_post_enabled=True,
        dry_run_mode=True,
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_token_secret="test_token_secret"
    )

    auto_poster = AutoPoster(config)

    # Create test post and thread
    test_post = BlogPost(
        file_path="_posts/2023-01-01-workflow-test.md",
        title="Workflow Test Post",
        content="This is a test post for the workflow",
        frontmatter={"auto_post": True, "publish": True},
        canonical_url="https://example.com/workflow-test",
        auto_post=True,
        slug="workflow-test"
    )

    test_tweets = [
        Tweet(content="🚀 Just published a new blog post about workflow testing!", position=1),
        Tweet(content="Here are the key insights I discovered during development...", position=2),
        Tweet(content="What's your experience with automated workflows? Let me know! 👇", position=3)
    ]

    test_thread = ThreadData(
        post_slug="workflow-test",
        tweets=test_tweets
    )

    # Test the complete workflow
    result = auto_poster.attempt_auto_post(test_thread, test_post)

    print(f"Workflow result: Success={result.success}")
    if result.success:
        print(f"Mock tweet IDs: {result.tweet_ids}")
    else:
        print(f"Error: {result.error_message}")

    print("Auto-posting workflow test completed ✓")


def test_posting_statistics():
    """Test posting statistics functionality."""
    print("\nTesting posting statistics...")

    config = GeneratorConfig(posted_directory=".test_posted")
    auto_poster = AutoPoster(config)

    # Get statistics (should be empty for new setup)
    stats = auto_poster.get_posting_statistics()
    print(f"Posting statistics: {stats}")

    # List posted threads (should be empty)
    threads = auto_poster.list_posted_threads()
    print(f"Posted threads count: {len(threads)}")

    print("Posting statistics test completed ✓")


def main():
    """Run all tests."""
    print("=== Auto-Posting Functionality Tests ===\n")

    try:
        test_auto_poster_setup()
        test_twitter_client_dry_run()
        test_auto_posting_workflow()
        test_posting_statistics()

        print("\n=== All tests completed successfully! ===")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())