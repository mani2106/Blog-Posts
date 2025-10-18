#!/usr/bin/env python3
"""
Comprehensive Test Data Sets for GitHub Tweet Thread Generator
Provides various blog content scenarios for testing all functionality.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any

class TestDataSets:
    """Comprehensive test data for various blog content scenarios."""

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.test_data_dir = os.path.join(self.base_path, 'test_data')
        os.makedirs(self.test_data_dir, exist_ok=True)

    def get_technical_tutorial_post(self) -> Dict[str, Any]:
        """Technical tutorial blog post for testing."""
        return {
            'file_path': '_posts/2024-01-15-advanced-python-decorators.md',
            'frontmatter': {
                'title': 'Advanced Python Decorators: A Complete Guide',
                'date': '2024-01-15',
                'categories': ['python', 'programming', 'tutorial'],
                'tags': ['decorators', 'advanced', 'python'],
                'summary': 'Learn how to create and use advanced Python decorators for cleaner, more maintainable code.',
                'publish': True,
                'auto_post': True,
                'canonical_url': 'https://example.com/advanced-python-decorators'
            },
            'content': '''# Advanced Python Decorators: A Complete Guide

Python decorators are one of the most powerful features of the language, yet many developers only scratch the surface of what's possible. In this comprehensive guide, we'll explore advanced decorator patterns that will transform how you write Python code.

## What Are Decorators Really?

At their core, decorators are functions that modify other functions. They follow the principle of "wrapping" functionality around existing code without modifying the original function.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@my_decorator
def greet(name):
    return f"Hello, {name}!"
```

## Advanced Patterns

### 1. Decorators with Arguments

```python
def retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
        return wrapper
    return decorator
```

### 2. Class-Based Decorators

```python
class RateLimiter:
    def __init__(self, max_calls=10, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls
            self.calls = [call_time for call_time in self.calls
                         if now - call_time < self.time_window]

            if len(self.calls) >= self.max_calls:
                raise Exception("Rate limit exceeded")

            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper
```

## Real-World Applications

I've used these patterns in production systems to:
- Implement automatic retry logic for API calls
- Add caching to expensive database queries
- Create rate limiting for user-facing endpoints
- Build comprehensive logging and monitoring

The key insight is that decorators allow you to separate concerns cleanly. Your business logic stays focused, while cross-cutting concerns like logging, caching, and error handling are handled elegantly by decorators.

## Best Practices

1. **Preserve function metadata** using `functools.wraps`
2. **Handle edge cases** like exceptions and return values
3. **Make decorators configurable** with parameters
4. **Test thoroughly** - decorators can hide bugs

## Conclusion

Mastering advanced decorator patterns will make you a more effective Python developer. They're not just syntactic sugar - they're a powerful tool for writing cleaner, more maintainable code.

What decorator patterns have you found most useful? Share your experiences in the comments!''',
            'expected_hooks': [
                'curiosity_gap',
                'value_proposition',
                'contrarian_take'
            ],
            'expected_engagement_elements': [
                'numbered_list',
                'code_examples',
                'personal_anecdote',
                'call_to_action'
            ]
        }

    def get_personal_experience_post(self) -> Dict[str, Any]:
        """Personal experience blog post for testing."""
        return {
            'file_path': '_posts/2024-02-10-my-journey-to-senior-developer.md',
            'frontmatter': {
                'title': 'My Journey from Junior to Senior Developer: 5 Hard-Learned Lessons',
                'date': '2024-02-10',
                'categories': ['career', 'personal', 'development'],
                'tags': ['career-growth', 'lessons-learned', 'senior-developer'],
                'summary': 'Five crucial lessons I learned on my path from junior to senior developer.',
                'publish': True,
                'auto_post': False,
                'canonical_url': 'https://example.com/journey-to-senior-developer'
            },
            'content': '''# My Journey from Junior to Senior Developer: 5 Hard-Learned Lessons

Three years ago, I was a junior developer struggling with imposter syndrome and wondering if I'd ever feel confident in my abilities. Today, I'm a senior developer leading a team of eight engineers. Here are the five most important lessons I learned along the way.

## Lesson 1: Code Quality Matters More Than Speed

Early in my career, I thought being fast was everything. I'd rush through features, skip tests, and leave technical debt for "later." This backfired spectacularly when a critical bug I introduced took down our main service for 4 hours.

That incident taught me that sustainable development is about writing code that works reliably, not just code that works right now.

## Lesson 2: Communication Is Your Superpower

The biggest difference between junior and senior developers isn't technical skill - it's communication. Senior developers:

- Explain complex concepts simply
- Ask the right questions before coding
- Document their decisions
- Give constructive feedback
- Know when to say "I don't know"

I spent months improving my communication skills, and it transformed my career more than any technical course ever did.

## Lesson 3: Learn the Business, Not Just the Code

Understanding why you're building something is as important as knowing how to build it. I started attending product meetings, talking to customers, and learning about our business metrics.

This shift in perspective helped me:
- Make better technical decisions
- Propose solutions that actually solve problems
- Become a trusted advisor to product managers
- Identify opportunities for improvement

## Lesson 4: Mentoring Others Accelerates Your Growth

When I started mentoring junior developers, I thought I was just helping them. But teaching forced me to:
- Articulate my thought processes clearly
- Question my own assumptions
- Stay current with best practices
- Develop leadership skills

The best way to solidify your knowledge is to teach it to someone else.

## Lesson 5: Embrace Failure as Learning

My biggest failures became my greatest teachers:
- The production outage taught me about monitoring and testing
- The missed deadline taught me about estimation and scope management
- The team conflict taught me about emotional intelligence

Every senior developer has a collection of war stories. The difference is learning from them instead of being paralyzed by them.

## The Real Secret

Here's what nobody tells you: becoming a senior developer isn't about reaching some magical level of technical expertise. It's about developing judgment, empathy, and the ability to see the bigger picture.

You don't need to know everything. You need to know how to learn, how to communicate, and how to make good decisions with incomplete information.

## What's Next?

If you're on this journey yourself, remember:
- Progress isn't always linear
- Everyone's path is different
- Imposter syndrome never fully goes away
- The learning never stops

What lessons have shaped your development career? I'd love to hear your stories!''',
            'expected_hooks': [
                'story_hook',
                'transformation_hook',
                'numbered_list_hook'
            ],
            'expected_engagement_elements': [
                'personal_story',
                'numbered_lessons',
                'relatable_struggles',
                'call_to_action'
            ]
        }

    def get_data_science_post(self) -> Dict[str, Any]:
        """Data science blog post for testing."""
        return {
            'file_path': '_posts/2024-03-05-machine-learning-production-mistakes.md',
            'frontmatter': {
                'title': '7 Machine Learning Production Mistakes That Cost Us $50K',
                'date': '2024-03-05',
                'categories': ['machine-learning', 'data-science', 'production'],
                'tags': ['ml-ops', 'production', 'mistakes', 'lessons'],
                'summary': 'Expensive lessons learned from deploying ML models in production.',
                'publish': True,
                'auto_post': True,
                'canonical_url': 'https://example.com/ml-production-mistakes'
            },
            'content': '''# 7 Machine Learning Production Mistakes That Cost Us $50K

Last year, our ML team made several costly mistakes when deploying models to production. Here's what went wrong and how you can avoid the same pitfalls.

## Mistake #1: No Data Drift Monitoring ($15K Loss)

We deployed a customer churn prediction model that worked perfectly in testing. Six months later, we discovered it was making terrible predictions because customer behavior had shifted during the pandemic.

**The Fix:** Implement data drift monitoring from day one. Monitor feature distributions, prediction confidence, and business metrics.

## Mistake #2: Ignoring Model Bias ($12K Loss)

Our hiring recommendation model showed bias against certain demographic groups. We only discovered this after a candidate complained, leading to legal fees and reputation damage.

**The Fix:** Test for bias across all protected characteristics. Use fairness metrics like demographic parity and equalized odds.

## Mistake #3: Poor Feature Engineering Pipeline ($8K Loss)

Our feature pipeline broke silently, feeding the model stale data for weeks. The model kept running but made increasingly poor predictions.

**The Fix:** Add comprehensive monitoring to your feature pipeline. Alert on missing data, stale features, and unexpected distributions.

## Mistake #4: No A/B Testing Framework ($7K Loss)

We deployed a new recommendation algorithm to all users at once. When conversion rates dropped 15%, we had no way to quickly roll back or understand the impact.

**The Fix:** Always deploy ML models with proper A/B testing. Start with a small percentage of traffic and gradually increase.

## Mistake #5: Inadequate Model Versioning ($5K Loss)

When our model started performing poorly, we couldn't quickly identify which version was causing issues or roll back to a previous version.

**The Fix:** Implement proper ML model versioning with tools like MLflow or DVC. Track model artifacts, code, and data versions together.

## Mistake #6: Missing Business Logic Validation ($2K Loss)

Our pricing model occasionally suggested negative prices due to edge cases we hadn't considered during training.

**The Fix:** Add business logic validation to all model outputs. Set reasonable bounds and sanity checks.

## Mistake #7: No Explainability for Stakeholders ($1K Loss)

When stakeholders questioned model decisions, we couldn't explain why the model made specific predictions, leading to loss of trust.

**The Fix:** Implement model explainability tools like SHAP or LIME. Create dashboards that business users can understand.

## The Real Cost

The financial cost was significant, but the real damage was to team morale and stakeholder trust. It took months to rebuild confidence in our ML systems.

## Key Takeaways

1. **Monitor everything** - data, models, and business metrics
2. **Test for bias** early and often
3. **Start small** with A/B testing
4. **Version everything** - models, data, and code
5. **Add guardrails** with business logic validation
6. **Make models explainable** from the start
7. **Build trust** through transparency and reliability

## Moving Forward

We've since implemented a comprehensive ML ops framework that prevents these issues. Our models are more reliable, our stakeholders trust our work, and we sleep better at night.

What ML production mistakes have you encountered? Share your experiences - let's learn from each other's failures!''',
            'expected_hooks': [
                'statistic_hook',
                'mistake_hook',
                'cost_hook'
            ],
            'expected_engagement_elements': [
                'numbered_mistakes',
                'financial_impact',
                'practical_solutions',
                'call_to_action'
            ]
        }

    def get_short_tip_post(self) -> Dict[str, Any]:
        """Short tip/trick blog post for testing."""
        return {
            'file_path': '_posts/2024-04-01-git-aliases-productivity.md',
            'frontmatter': {
                'title': '5 Git Aliases That Will 10x Your Productivity',
                'date': '2024-04-01',
                'categories': ['git', 'productivity', 'tips'],
                'tags': ['git', 'aliases', 'productivity', 'workflow'],
                'summary': 'Simple Git aliases that will dramatically speed up your development workflow.',
                'publish': True,
                'auto_post': True,
                'canonical_url': 'https://example.com/git-aliases-productivity'
            },
            'content': '''# 5 Git Aliases That Will 10x Your Productivity

Stop typing the same long Git commands over and over. These 5 aliases will transform your workflow.

## 1. Super Status
```bash
git config --global alias.s "status -sb"
```
Instead of `git status`, just type `git s` for a clean, branch-aware status.

## 2. Pretty Logs
```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
```
`git lg` gives you a beautiful, visual commit history.

## 3. Quick Commit
```bash
git config --global alias.ac "!git add -A && git commit -m"
```
`git ac "message"` stages everything and commits in one command.

## 4. Undo Last Commit
```bash
git config --global alias.undo "reset HEAD~1 --mixed"
```
`git undo` safely undoes your last commit while keeping changes.

## 5. Branch Cleanup
```bash
git config --global alias.cleanup "!git branch --merged | grep -v '\\*\\|master\\|main' | xargs -n 1 git branch -d"
```
`git cleanup` removes all merged branches automatically.

## Bonus: My Complete .gitconfig

Here's my full alias section:
```bash
[alias]
    s = status -sb
    lg = log --oneline --graph --decorate --all
    ac = !git add -A && git commit -m
    undo = reset HEAD~1 --mixed
    cleanup = !git branch --merged | grep -v '\\*\\|master\\|main' | xargs -n 1 git branch -d
    co = checkout
    br = branch
    ci = commit
    st = status
```

These aliases have saved me hours every week. Set them up once, benefit forever.

What are your favorite Git aliases? Share them below!''',
            'expected_hooks': [
                'productivity_hook',
                'value_proposition_hook',
                'numbered_list_hook'
            ],
            'expected_engagement_elements': [
                'code_examples',
                'numbered_tips',
                'practical_value',
                'call_to_action'
            ]
        }

    def get_controversial_opinion_post(self) -> Dict[str, Any]:
        """Controversial opinion post for testing."""
        return {
            'file_path': '_posts/2024-05-15-unit-tests-are-overrated.md',
            'frontmatter': {
                'title': 'Unpopular Opinion: Unit Tests Are Overrated (And Here\'s What to Do Instead)',
                'date': '2024-05-15',
                'categories': ['testing', 'opinion', 'software-development'],
                'tags': ['testing', 'unit-tests', 'integration-tests', 'controversial'],
                'summary': 'Why I think unit tests are overrated and what testing strategy actually works.',
                'publish': True,
                'auto_post': False,
                'canonical_url': 'https://example.com/unit-tests-overrated'
            },
            'content': '''# Unpopular Opinion: Unit Tests Are Overrated (And Here's What to Do Instead)

I'm about to say something that will make many developers angry: unit tests are overrated, and the obsession with 100% unit test coverage is hurting software quality.

Before you close this tab in rage, hear me out.

## The Unit Test Obsession Problem

I've worked on codebases with 95% unit test coverage that were still riddled with bugs. I've seen teams spend 60% of their time writing and maintaining unit tests that test implementation details rather than behavior.

The problem isn't unit tests themselves - it's the cargo cult mentality around them.

## What's Wrong with Pure Unit Testing

### 1. They Test Implementation, Not Behavior
Most unit tests are tightly coupled to implementation details. Change how a function works internally, and half your tests break - even if the behavior is identical.

### 2. They Give False Confidence
High unit test coverage doesn't mean your system works. It means your individual functions work in isolation, which isn't how software actually runs.

### 3. They're Expensive to Maintain
Every refactor becomes a nightmare of updating dozens of unit tests that are testing the wrong things.

## What Actually Works: The Testing Pyramid Flip

Instead of the traditional testing pyramid, I use an inverted approach:

### 70% Integration Tests
Test how your components work together. These catch the bugs that actually matter to users.

### 20% End-to-End Tests
Test critical user journeys. If these pass, your app works for real users.

### 10% Unit Tests
Only for complex algorithms and pure functions with clear inputs/outputs.

## Real-World Example

At my last company, we had a payment processing service with:
- 200 unit tests (all passing)
- 5 integration tests
- 2 end-to-end tests

Guess which tests caught the bug that would have charged customers twice? The integration tests.

The unit tests were useless because they mocked away all the interesting interactions.

## What to Test Instead

Focus on:
1. **Contract tests** - API boundaries and data formats
2. **Integration tests** - How services work together
3. **Property-based tests** - Generate random inputs to find edge cases
4. **Smoke tests** - Critical paths through your system

## The Controversial Part

Here's what really makes developers angry: **delete your brittle unit tests**.

If a test breaks every time you refactor without finding real bugs, it's not helping. It's technical debt.

## When Unit Tests Make Sense

Don't get me wrong - unit tests have their place:
- Complex algorithms
- Pure functions
- Edge case handling
- Business logic with clear rules

But testing that `getUserById(123)` calls the database with the right parameters? That's not valuable.

## The Real Goal

The goal isn't test coverage. It's confidence that your system works correctly.

I'd rather have 10 well-written integration tests that verify real user scenarios than 100 unit tests that mock everything and test nothing meaningful.

## My Testing Philosophy

1. **Test behavior, not implementation**
2. **Write tests that would fail if the feature broke**
3. **Prefer integration over isolation**
4. **Delete tests that don't add value**
5. **Focus on user-facing functionality**

## The Backlash

I know this post will generate controversy. Developers are passionate about testing, and challenging the unit test orthodoxy feels like heresy.

But I've seen too many teams waste time on meaningless tests while shipping buggy software.

## What Do You Think?

Am I completely wrong? Have you found unit tests invaluable? Or have you also struggled with brittle, high-maintenance test suites?

Let's have a respectful debate in the comments. I'm genuinely curious about your experiences.''',
            'expected_hooks': [
                'contrarian_hook',
                'controversial_hook',
                'opinion_hook'
            ],
            'expected_engagement_elements': [
                'controversial_stance',
                'personal_experience',
                'numbered_points',
                'call_to_action'
            ]
        }

    def get_jupyter_notebook_post(self) -> Dict[str, Any]:
        """Jupyter notebook blog post for testing."""
        return {
            'file_path': '_notebooks/2024-06-01-data-visualization-matplotlib.ipynb',
            'frontmatter': {
                'title': 'Beautiful Data Visualizations with Matplotlib: A Step-by-Step Guide',
                'date': '2024-06-01',
                'categories': ['data-science', 'visualization', 'python'],
                'tags': ['matplotlib', 'data-viz', 'python', 'tutorial'],
                'summary': 'Learn to create stunning data visualizations using Matplotlib with practical examples.',
                'publish': True,
                'auto_post': True,
                'canonical_url': 'https://example.com/matplotlib-visualization-guide'
            },
            'content': '''This notebook demonstrates advanced Matplotlib techniques for creating publication-quality visualizations.

We'll cover:
1. Setting up the perfect plotting environment
2. Creating multi-panel figures
3. Customizing colors and styles
4. Adding annotations and callouts
5. Exporting high-resolution figures

The key to great data visualization is telling a story with your data. Every chart should have a clear message and guide the viewer's attention to the most important insights.

By the end of this tutorial, you'll be able to create visualizations that not only look professional but effectively communicate your findings.''',
            'expected_hooks': [
                'tutorial_hook',
                'step_by_step_hook',
                'value_proposition_hook'
            ],
            'expected_engagement_elements': [
                'numbered_steps',
                'practical_examples',
                'visual_content',
                'learning_outcome'
            ]
        }

    def get_style_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Sample style profiles for different author types."""
        return {
            'technical_blogger': {
                'vocabulary_patterns': {
                    'technical_terms': ['implementation', 'architecture', 'optimization', 'scalability'],
                    'common_words': ['system', 'code', 'function', 'data', 'performance'],
                    'complexity_level': 'high'
                },
                'tone_indicators': {
                    'formality': 'professional',
                    'enthusiasm': 'moderate',
                    'confidence': 'high',
                    'teaching_style': 'explanatory'
                },
                'content_structures': {
                    'preferred_formats': ['numbered_lists', 'code_examples', 'step_by_step'],
                    'average_section_length': 150,
                    'uses_subheadings': True
                },
                'emoji_usage': {
                    'frequency': 'low',
                    'types': ['🚀', '⚡', '🔧', '💡']
                }
            },
            'personal_blogger': {
                'vocabulary_patterns': {
                    'personal_pronouns': ['I', 'my', 'me', 'we'],
                    'emotional_words': ['excited', 'frustrated', 'learned', 'discovered'],
                    'complexity_level': 'medium'
                },
                'tone_indicators': {
                    'formality': 'casual',
                    'enthusiasm': 'high',
                    'confidence': 'moderate',
                    'teaching_style': 'storytelling'
                },
                'content_structures': {
                    'preferred_formats': ['stories', 'lessons_learned', 'personal_anecdotes'],
                    'average_section_length': 120,
                    'uses_subheadings': True
                },
                'emoji_usage': {
                    'frequency': 'medium',
                    'types': ['😊', '🎉', '💭', '🌟', '🚀']
                }
            },
            'data_science_blogger': {
                'vocabulary_patterns': {
                    'technical_terms': ['model', 'algorithm', 'dataset', 'prediction', 'analysis'],
                    'statistical_terms': ['correlation', 'regression', 'distribution', 'variance'],
                    'complexity_level': 'high'
                },
                'tone_indicators': {
                    'formality': 'professional',
                    'enthusiasm': 'moderate',
                    'confidence': 'high',
                    'teaching_style': 'analytical'
                },
                'content_structures': {
                    'preferred_formats': ['methodology', 'results', 'code_examples', 'visualizations'],
                    'average_section_length': 180,
                    'uses_subheadings': True
                },
                'emoji_usage': {
                    'frequency': 'low',
                    'types': ['📊', '📈', '🔍', '💡', '⚡']
                }
            }
        }

    def get_mock_api_responses(self) -> Dict[str, Any]:
        """Mock API responses for testing."""
        return {
            'openrouter_thread_generation': {
                'choices': [{
                    'message': {
                        'content': json.dumps({
                            'hook_variations': [
                                "🧵 THREAD: The Python decorator pattern that changed how I write code",
                                "What if I told you there's a Python feature that can 10x your code quality?",
                                "Most developers use decorators wrong. Here's the right way:"
                            ],
                            'tweets': [
                                "🧵 THREAD: The Python decorator pattern that changed how I write code\n\nDecorators aren't just syntactic sugar - they're a powerful tool for writing cleaner, more maintainable code.\n\nHere's what I wish I knew when I started: 🧵1/7",
                                "At their core, decorators are functions that modify other functions.\n\nThey follow the principle of \"wrapping\" functionality around existing code without modifying the original function.\n\nThink of them as code enhancers. 🧵2/7",
                                "Here's a simple example:\n\n```python\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print(f\"Calling {func.__name__}\")\n        result = func(*args, **kwargs)\n        return result\n    return wrapper\n```\n\n🧵3/7",
                                "But the real power comes with advanced patterns:\n\n✅ Decorators with arguments\n✅ Class-based decorators  \n✅ Chaining multiple decorators\n✅ Preserving function metadata\n\nEach pattern solves different problems. 🧵4/7",
                                "I've used these patterns in production to:\n\n• Implement automatic retry logic for API calls\n• Add caching to expensive database queries\n• Create rate limiting for endpoints\n• Build comprehensive logging\n\nThey separate concerns beautifully. 🧵5/7",
                                "The key insight: decorators allow you to keep business logic focused while handling cross-cutting concerns elegantly.\n\nYour functions do one thing well, decorators handle the rest.\n\nThis is the path to maintainable code. 🧵6/7",
                                "Best practices:\n\n1. Use functools.wraps to preserve metadata\n2. Handle edge cases and exceptions\n3. Make decorators configurable\n4. Test thoroughly\n\nWhat decorator patterns have you found most useful?\n\nShare your experiences! 🧵7/7"
                            ],
                            'hashtags': ['#Python', '#Programming']
                        })
                    }
                }]
            },
            'github_pr_creation': {
                'number': 123,
                'html_url': 'https://github.com/user/repo/pull/123',
                'title': 'Generated tweet thread for: Advanced Python Decorators'
            },
            'twitter_thread_posting': {
                'tweet_ids': ['1234567890', '1234567891', '1234567892'],
                'success': True
            }
        }

    def create_test_repository_structure(self):
        """Create a complete test repository structure."""
        repo_structure = {
            '_posts': [
                self.get_technical_tutorial_post(),
                self.get_personal_experience_post(),
                self.get_data_science_post(),
                self.get_short_tip_post(),
                self.get_controversial_opinion_post()
            ],
            '_notebooks': [
                self.get_jupyter_notebook_post()
            ],
            '.generated': {
                'writing-style-profile.json': self.get_style_profiles()['technical_blogger']
            },
            '.posted': {},
            '_config.yml': {
                'title': 'Test Blog',
                'description': 'A test blog for the tweet generator',
                'url': 'https://test-blog.github.io'
            }
        }

        # Create the directory structure
        test_repo_dir = os.path.join(self.test_data_dir, 'test_repository')
        os.makedirs(test_repo_dir, exist_ok=True)

        for directory, content in repo_structure.items():
            dir_path = os.path.join(test_repo_dir, directory)
            os.makedirs(dir_path, exist_ok=True)

            if isinstance(content, list):
                # Handle posts/notebooks
                for item in content:
                    filename = os.path.basename(item['file_path'])
                    file_path = os.path.join(dir_path, filename)

                    # Create frontmatter content
                    frontmatter_lines = ['---']
                    for key, value in item['frontmatter'].items():
                        if isinstance(value, list):
                            frontmatter_lines.append(f'{key}:')
                            for v in value:
                                frontmatter_lines.append(f'  - {v}')
                        else:
                            frontmatter_lines.append(f'{key}: {value}')
                    frontmatter_lines.append('---\n')

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(frontmatter_lines))
                        f.write(item['content'])

            elif isinstance(content, dict):
                # Handle configuration files
                for filename, file_content in content.items():
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if filename.endswith('.json'):
                            json.dump(file_content, f, indent=2)
                        elif isinstance(file_content, dict):
                            # YAML content
                            for key, value in file_content.items():
                                f.write(f'{key}: {value}\n')
                        else:
                            # String content
                            f.write(str(file_content))

        return test_repo_dir

    def get_performance_test_scenarios(self) -> List[Dict[str, Any]]:
        """Performance test scenarios with expected benchmarks."""
        return [
            {
                'name': 'style_analysis_small_blog',
                'description': 'Style analysis with 5 blog posts',
                'post_count': 5,
                'expected_max_time': 10.0,  # seconds
                'expected_max_memory': 100  # MB
            },
            {
                'name': 'style_analysis_medium_blog',
                'description': 'Style analysis with 25 blog posts',
                'post_count': 25,
                'expected_max_time': 30.0,
                'expected_max_memory': 200
            },
            {
                'name': 'style_analysis_large_blog',
                'description': 'Style analysis with 100 blog posts',
                'post_count': 100,
                'expected_max_time': 120.0,
                'expected_max_memory': 500
            },
            {
                'name': 'thread_generation_simple',
                'description': 'Thread generation for short post',
                'content_length': 500,
                'expected_max_time': 15.0,
                'expected_max_memory': 50
            },
            {
                'name': 'thread_generation_complex',
                'description': 'Thread generation for long technical post',
                'content_length': 5000,
                'expected_max_time': 30.0,
                'expected_max_memory': 100
            },
            {
                'name': 'end_to_end_workflow',
                'description': 'Complete workflow from detection to PR creation',
                'post_count': 3,
                'expected_max_time': 60.0,
                'expected_max_memory': 200
            }
        ]

    def save_all_test_data(self):
        """Save all test data to files for use by test suites."""
        # Save individual test posts
        posts = [
            ('technical_tutorial', self.get_technical_tutorial_post()),
            ('personal_experience', self.get_personal_experience_post()),
            ('data_science', self.get_data_science_post()),
            ('short_tip', self.get_short_tip_post()),
            ('controversial_opinion', self.get_controversial_opinion_post()),
            ('jupyter_notebook', self.get_jupyter_notebook_post())
        ]

        for name, post_data in posts:
            file_path = os.path.join(self.test_data_dir, f'{name}_post.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, default=str)

        # Save style profiles
        style_profiles_path = os.path.join(self.test_data_dir, 'style_profiles.json')
        with open(style_profiles_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_style_profiles(), f, indent=2)

        # Save mock API responses
        mock_responses_path = os.path.join(self.test_data_dir, 'mock_api_responses.json')
        with open(mock_responses_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_mock_api_responses(), f, indent=2)

        # Save performance scenarios
        performance_scenarios_path = os.path.join(self.test_data_dir, 'performance_scenarios.json')
        with open(performance_scenarios_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_performance_test_scenarios(), f, indent=2, default=str)

        # Create test repository structure
        self.create_test_repository_structure()

        print(f"Test data saved to: {self.test_data_dir}")
        return self.test_data_dir


def main():
    """Generate and save all test data sets."""
    test_data = TestDataSets()
    test_data.save_all_test_data()
    print("✅ All test data sets created successfully!")


if __name__ == "__main__":
    main()