#!/usr/bin/env python3
"""
Mock Services for External API Testing
Provides mock implementations of OpenRouter, GitHub, and Twitter APIs for testing.
"""

import json
import time
import random
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
from datetime import datetime

class MockOpenRouterAPI:
    """Mock implementation of OpenRouter API for testing."""

    def __init__(self):
        self.call_count = 0
        self.last_request = None
        self.response_delay = 0.1  # Simulate API latency
        self.failure_rate = 0.0  # Simulate API failures
        self.rate_limit_remaining = 1000

    def set_failure_rate(self, rate: float):
        """Set the failure rate for API calls (0.0 to 1.0)."""
        self.failure_rate = rate

    def set_response_delay(self, delay: float):
        """Set the response delay in seconds."""
        self.response_delay = delay

    def generate_thread_response(self, prompt: str, model: str = "anthropic/claude-3-haiku") -> Dict[str, Any]:
        """Generate a mock thread response."""
        time.sleep(self.response_delay)
        self.call_count += 1
        self.last_request = {'prompt': prompt, 'model': model}

        # Simulate API failures
        if random.random() < self.failure_rate:
            raise Exception("OpenRouter API Error: Rate limit exceeded")

        # Generate different responses based on content type
        if "python" in prompt.lower() or "code" in prompt.lower():
            return self._generate_technical_thread()
        elif "personal" in prompt.lower() or "journey" in prompt.lower():
            return self._generate_personal_thread()
        elif "data" in prompt.lower() or "machine learning" in prompt.lower():
            return self._generate_data_science_thread()
        else:
            return self._generate_generic_thread()

    def _generate_technical_thread(self) -> Dict[str, Any]:
        """Generate a technical thread response."""
        return {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'hook_variations': [
                            "🧵 THREAD: The Python pattern that changed how I write code",
                            "What if I told you there's a Python feature that can 10x your code quality?",
                            "Most developers use this Python feature wrong. Here's the right way:"
                        ],
                        'tweets': [
                            "🧵 THREAD: The Python pattern that changed how I write code\n\nThis isn't just syntactic sugar - it's a powerful tool for writing cleaner, more maintainable code.\n\nHere's what I wish I knew when I started: 🧵1/6",
                            "The key insight: this pattern allows you to separate concerns cleanly.\n\nYour business logic stays focused, while cross-cutting concerns are handled elegantly.\n\nThis is the path to maintainable code. 🧵2/6",
                            "Here's a practical example:\n\n```python\n# Clean, focused code\n@decorator\ndef process_data(data):\n    return transform(data)\n```\n\nThe decorator handles logging, caching, error handling. 🧵3/6",
                            "I've used this pattern in production to:\n\n• Implement automatic retry logic\n• Add caching to expensive operations\n• Create comprehensive logging\n• Build rate limiting\n\nEach solves different problems. 🧵4/6",
                            "Best practices I've learned:\n\n1. Preserve function metadata\n2. Handle edge cases properly\n3. Make decorators configurable\n4. Test thoroughly\n\nThese patterns have saved me hours every week. 🧵5/6",
                            "The real power comes from composition - chaining multiple patterns together for complex behaviors.\n\nWhat patterns have you found most useful?\n\nShare your experiences! 🧵6/6"
                        ],
                        'hashtags': ['#Python', '#Programming']
                    })
                }
            }],
            'usage': {
                'prompt_tokens': 150,
                'completion_tokens': 300,
                'total_tokens': 450
            }
        }

    def _generate_personal_thread(self) -> Dict[str, Any]:
        """Generate a personal experience thread response."""
        return {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'hook_variations': [
                            "🧵 My journey from junior to senior developer: 5 hard-learned lessons",
                            "Three years ago, I was struggling with imposter syndrome. Today, I lead a team of 8.",
                            "The 5 lessons that transformed my development career:"
                        ],
                        'tweets': [
                            "🧵 My journey from junior to senior developer: 5 hard-learned lessons\n\nThree years ago, I was struggling with imposter syndrome. Today, I lead a team of 8 engineers.\n\nHere's what changed everything: 🧵1/7",
                            "Lesson 1: Code quality matters more than speed\n\nEarly on, I thought being fast was everything. I'd rush through features and skip tests.\n\nThis backfired when a critical bug took down our service for 4 hours. 🧵2/7",
                            "Lesson 2: Communication is your superpower\n\nThe biggest difference between junior and senior developers isn't technical skill - it's communication.\n\nSenior developers explain complex concepts simply. 🧵3/7",
                            "Lesson 3: Learn the business, not just the code\n\nUnderstanding why you're building something is as important as knowing how.\n\nThis helped me make better technical decisions and become a trusted advisor. 🧵4/7",
                            "Lesson 4: Mentoring others accelerates your growth\n\nTeaching forced me to articulate my thought processes and question my assumptions.\n\nThe best way to solidify knowledge is to teach it. 🧵5/7",
                            "Lesson 5: Embrace failure as learning\n\nMy biggest failures became my greatest teachers:\n• Production outages taught me about monitoring\n• Missed deadlines taught me estimation\n• Team conflicts taught me emotional intelligence 🧵6/7",
                            "The real secret: becoming senior isn't about technical expertise.\n\nIt's about developing judgment, empathy, and seeing the bigger picture.\n\nWhat lessons have shaped your career? 🧵7/7"
                        ],
                        'hashtags': ['#CareerGrowth', '#SoftwareDevelopment']
                    })
                }
            }],
            'usage': {
                'prompt_tokens': 200,
                'completion_tokens': 350,
                'total_tokens': 550
            }
        }

    def _generate_data_science_thread(self) -> Dict[str, Any]:
        """Generate a data science thread response."""
        return {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'hook_variations': [
                            "🧵 7 ML production mistakes that cost us $50K",
                            "Our ML team made expensive mistakes deploying models. Here's what went wrong:",
                            "The 7 most costly ML production mistakes (and how to avoid them):"
                        ],
                        'tweets': [
                            "🧵 7 ML production mistakes that cost us $50K\n\nLast year, our ML team made several costly mistakes deploying models to production.\n\nHere's what went wrong and how to avoid it: 🧵1/8",
                            "Mistake #1: No data drift monitoring ($15K loss)\n\nWe deployed a churn prediction model that worked perfectly in testing.\n\n6 months later, it was making terrible predictions because customer behavior had shifted. 🧵2/8",
                            "Mistake #2: Ignoring model bias ($12K loss)\n\nOur hiring model showed bias against certain groups. We only discovered this after a complaint.\n\nAlways test for bias across protected characteristics. 🧵3/8",
                            "Mistake #3: Poor feature pipeline ($8K loss)\n\nOur feature pipeline broke silently, feeding stale data for weeks.\n\nThe model kept running but predictions got worse and worse. 🧵4/8",
                            "Mistake #4: No A/B testing ($7K loss)\n\nWe deployed a new recommendation algorithm to all users at once.\n\nWhen conversion rates dropped 15%, we had no way to quickly roll back. 🧵5/8",
                            "Mistake #5: Inadequate versioning ($5K loss)\n\nWhen performance degraded, we couldn't identify which model version was causing issues.\n\nImplement proper ML model versioning from day one. 🧵6/8",
                            "The real cost wasn't just financial - it was team morale and stakeholder trust.\n\nIt took months to rebuild confidence in our ML systems. 🧵7/8",
                            "Key takeaways:\n• Monitor everything\n• Test for bias\n• Start small with A/B testing\n• Version everything\n• Add guardrails\n• Make models explainable\n\nWhat ML mistakes have you encountered? 🧵8/8"
                        ],
                        'hashtags': ['#MachineLearning', '#DataScience']
                    })
                }
            }],
            'usage': {
                'prompt_tokens': 180,
                'completion_tokens': 400,
                'total_tokens': 580
            }
        }

    def _generate_generic_thread(self) -> Dict[str, Any]:
        """Generate a generic thread response."""
        return {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'hook_variations': [
                            "🧵 THREAD: Something interesting I learned recently",
                            "Here's a quick insight that might help you:",
                            "Let me share something that changed my perspective:"
                        ],
                        'tweets': [
                            "🧵 THREAD: Something interesting I learned recently\n\nThis insight changed how I approach problems.\n\nHere's what I discovered: 🧵1/4",
                            "The key insight is that small changes can have big impacts.\n\nIt's not about doing everything differently - it's about doing the right things better. 🧵2/4",
                            "I've applied this principle to:\n• Daily workflows\n• Problem-solving approaches\n• Team collaboration\n• Personal development\n\nEach area saw meaningful improvement. 🧵3/4",
                            "The takeaway: focus on fundamentals and compound improvements.\n\nSmall, consistent changes beat dramatic overhauls.\n\nWhat small changes have made a big difference for you? 🧵4/4"
                        ],
                        'hashtags': ['#Learning', '#Growth']
                    })
                }
            }],
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 200,
                'total_tokens': 300
            }
        }


class MockGitHubAPI:
    """Mock implementation of GitHub API for testing."""

    def __init__(self):
        self.repos = {}
        self.pulls = {}
        self.files = {}
        self.call_count = 0
        self.failure_rate = 0.0

    def set_failure_rate(self, rate: float):
        """Set the failure rate for API calls."""
        self.failure_rate = rate

    def create_mock_repo(self, owner: str, name: str) -> Mock:
        """Create a mock repository."""
        repo = Mock()
        repo.owner.login = owner
        repo.name = name
        repo.default_branch = 'main'
        repo.html_url = f'https://github.com/{owner}/{name}'

        self.repos[f'{owner}/{name}'] = repo
        return repo

    def create_mock_pull_request(self, repo_name: str, number: int, title: str) -> Mock:
        """Create a mock pull request."""
        if random.random() < self.failure_rate:
            raise Exception("GitHub API Error: Rate limit exceeded")

        pr = Mock()
        pr.number = number
        pr.title = title
        pr.html_url = f'https://github.com/{repo_name}/pull/{number}'
        pr.state = 'open'
        pr.created_at = datetime.now()
        pr.updated_at = datetime.now()

        self.pulls[f'{repo_name}#{number}'] = pr
        self.call_count += 1
        return pr

    def update_mock_pull_request(self, repo_name: str, number: int, **kwargs) -> Mock:
        """Update a mock pull request."""
        if random.random() < self.failure_rate:
            raise Exception("GitHub API Error: API rate limit exceeded")

        pr_key = f'{repo_name}#{number}'
        if pr_key in self.pulls:
            pr = self.pulls[pr_key]
            for key, value in kwargs.items():
                setattr(pr, key, value)
            pr.updated_at = datetime.now()
            self.call_count += 1
            return pr
        else:
            return self.create_mock_pull_request(repo_name, number, kwargs.get('title', 'Updated PR'))

    def create_mock_file(self, repo_name: str, path: str, content: str) -> Mock:
        """Create a mock file in the repository."""
        if random.random() < self.failure_rate:
            raise Exception("GitHub API Error: Repository access denied")

        file_obj = Mock()
        file_obj.path = path
        file_obj.content = content
        file_obj.sha = f'sha_{hash(content)}'

        self.files[f'{repo_name}:{path}'] = file_obj
        self.call_count += 1
        return file_obj

    def get_mock_file_contents(self, repo_name: str, path: str) -> Mock:
        """Get mock file contents."""
        file_key = f'{repo_name}:{path}'
        if file_key in self.files:
            return self.files[file_key]
        else:
            # Return empty file
            return self.create_mock_file(repo_name, path, '')


class MockTwitterAPI:
    """Mock implementation of Twitter API for testing."""

    def __init__(self):
        self.tweets = {}
        self.call_count = 0
        self.failure_rate = 0.0
        self.rate_limit_remaining = 300
        self.posted_threads = []

    def set_failure_rate(self, rate: float):
        """Set the failure rate for API calls."""
        self.failure_rate = rate

    def post_tweet(self, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """Post a mock tweet."""
        if random.random() < self.failure_rate:
            raise Exception("Twitter API Error: Rate limit exceeded")

        tweet_id = f'tweet_{self.call_count + 1000000000}'
        tweet_data = {
            'id': tweet_id,
            'text': text,
            'created_at': datetime.now().isoformat(),
            'public_metrics': {
                'retweet_count': random.randint(0, 50),
                'like_count': random.randint(0, 200),
                'reply_count': random.randint(0, 20),
                'quote_count': random.randint(0, 10)
            }
        }

        if reply_to:
            tweet_data['in_reply_to_user_id'] = reply_to

        self.tweets[tweet_id] = tweet_data
        self.call_count += 1
        self.rate_limit_remaining -= 1

        return {'data': tweet_data}

    def post_thread(self, tweets: List[str]) -> List[Dict[str, Any]]:
        """Post a mock thread."""
        thread_results = []
        previous_tweet_id = None

        for tweet_text in tweets:
            result = self.post_tweet(tweet_text, reply_to=previous_tweet_id)
            thread_results.append(result)
            previous_tweet_id = result['data']['id']

        # Store thread for tracking
        thread_data = {
            'tweets': thread_results,
            'posted_at': datetime.now().isoformat(),
            'thread_id': thread_results[0]['data']['id']
        }
        self.posted_threads.append(thread_data)

        return thread_results

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get mock rate limit status."""
        return {
            'resources': {
                'tweets': {
                    '/2/tweets': {
                        'limit': 300,
                        'remaining': self.rate_limit_remaining,
                        'reset': int(time.time()) + 900  # 15 minutes from now
                    }
                }
            }
        }


class MockServiceFactory:
    """Factory for creating and managing mock services."""

    def __init__(self):
        self.openrouter = MockOpenRouterAPI()
        self.github = MockGitHubAPI()
        self.twitter = MockTwitterAPI()

    def reset_all_mocks(self):
        """Reset all mock services to initial state."""
        self.openrouter = MockOpenRouterAPI()
        self.github = MockGitHubAPI()
        self.twitter = MockTwitterAPI()

    def set_failure_scenario(self, service: str, failure_rate: float):
        """Set failure scenario for a specific service."""
        if service == 'openrouter':
            self.openrouter.set_failure_rate(failure_rate)
        elif service == 'github':
            self.github.set_failure_rate(failure_rate)
        elif service == 'twitter':
            self.twitter.set_failure_rate(failure_rate)
        elif service == 'all':
            self.openrouter.set_failure_rate(failure_rate)
            self.github.set_failure_rate(failure_rate)
            self.twitter.set_failure_rate(failure_rate)

    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics for all mock services."""
        return {
            'openrouter': {
                'call_count': self.openrouter.call_count,
                'last_request': self.openrouter.last_request
            },
            'github': {
                'call_count': self.github.call_count,
                'repos_created': len(self.github.repos),
                'prs_created': len(self.github.pulls),
                'files_created': len(self.github.files)
            },
            'twitter': {
                'call_count': self.twitter.call_count,
                'tweets_posted': len(self.twitter.tweets),
                'threads_posted': len(self.twitter.posted_threads),
                'rate_limit_remaining': self.twitter.rate_limit_remaining
            }
        }

    def create_test_scenario(self, scenario_name: str):
        """Create a specific test scenario with pre-configured mock data."""
        if scenario_name == 'successful_workflow':
            # Configure for successful end-to-end workflow
            self.set_failure_scenario('all', 0.0)
            self.openrouter.set_response_delay(0.1)

            # Pre-create a test repository
            repo = self.github.create_mock_repo('testuser', 'test-blog')

        elif scenario_name == 'api_failures':
            # Configure for API failure testing
            self.set_failure_scenario('all', 0.3)  # 30% failure rate

        elif scenario_name == 'rate_limiting':
            # Configure for rate limiting scenarios
            self.twitter.rate_limit_remaining = 5
            self.openrouter.rate_limit_remaining = 10

        elif scenario_name == 'slow_responses':
            # Configure for performance testing
            self.openrouter.set_response_delay(2.0)
            self.set_failure_scenario('all', 0.0)


# Global mock factory instance
mock_factory = MockServiceFactory()


def get_mock_services() -> MockServiceFactory:
    """Get the global mock services factory."""
    return mock_factory


def reset_mock_services():
    """Reset all mock services."""
    global mock_factory
    mock_factory.reset_all_mocks()


# Pytest fixtures for easy testing
def pytest_mock_openrouter():
    """Pytest fixture for OpenRouter mock."""
    return mock_factory.openrouter


def pytest_mock_github():
    """Pytest fixture for GitHub mock."""
    return mock_factory.github


def pytest_mock_twitter():
    """Pytest fixture for Twitter mock."""
    return mock_factory.twitter


if __name__ == "__main__":
    # Demo of mock services
    factory = MockServiceFactory()

    print("🧪 Mock Services Demo")
    print("=" * 50)

    # Test OpenRouter
    print("\n📡 Testing OpenRouter Mock:")
    response = factory.openrouter.generate_thread_response("Write about Python decorators")
    print(f"Generated {len(json.loads(response['choices'][0]['message']['content'])['tweets'])} tweets")

    # Test GitHub
    print("\n🐙 Testing GitHub Mock:")
    repo = factory.github.create_mock_repo('testuser', 'test-repo')
    pr = factory.github.create_mock_pull_request('testuser/test-repo', 123, 'Test PR')
    print(f"Created PR #{pr.number}: {pr.title}")

    # Test Twitter
    print("\n🐦 Testing Twitter Mock:")
    tweets = ["First tweet", "Second tweet", "Third tweet"]
    thread = factory.twitter.post_thread(tweets)
    print(f"Posted thread with {len(thread)} tweets")

    # Show stats
    print("\n📊 Service Statistics:")
    stats = factory.get_service_stats()
    for service, data in stats.items():
        print(f"{service}: {data}")

    print("\n✅ Mock services working correctly!")