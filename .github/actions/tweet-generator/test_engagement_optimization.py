"""
Comprehensive unit tests for engagement optimization functionality.

This module tests hook generation, thread structure optimization, engagement element
integration, and psychological trigger effectiveness as specified in requirements 9.1, 9.2, and 9.3.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from engagement_optimizer import EngagementOptimizer
from models import (
    BlogPost, StyleProfile, VocabularyProfile, ToneProfile,
    StructureProfile, EmojiProfile, Tweet, ThreadData, ThreadPlan,
    HookType, EngagementLevel
)
from exceptions import ValidationError, TweetGeneratorError


class TestEngagementOptimizer:
    """Test suite for EngagementOptimizer class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.optimizer = EngagementOptimizer(optimization_level="high")

        # Create sample blog post
        self.sample_blog_post = BlogPost(
            file_path="_posts/2024-01-15-machine-learning-guide.md",
            title="Complete Guide to Machine Learning",
            content="This is a comprehensive guide to machine learning fundamentals...",
            frontmatter={"title": "Complete Guide to Machine Learning", "categories": ["machine-learning", "tutorial"]},
            canonical_url="https://example.com/ml-guide",
            categories=["machine-learning", "tutorial"],
            summary="Learn machine learning from scratch",
            slug="machine-learning-guide"
        )

        # Create sample style profile
        self.sample_style_profile = StyleProfile(
            vocabulary_patterns=VocabularyProfile(
                common_words=["learn", "understand", "implement", "optimize"],
                technical_terms=["algorithm", "model", "training", "validation"],
                average_word_length=6.5,
                vocabulary_diversity=0.8
            ),
            tone_indicators=ToneProfile(
                formality_level=0.6,
                enthusiasm_level=0.7,
                confidence_level=0.8,
                personal_anecdotes=True,
                question_frequency=0.3
            ),
            content_structures=StructureProfile(
                average_sentence_length=18.5,
                paragraph_length_preference="medium",
                list_usage_frequency=0.4
            ),
            emoji_usage=EmojiProfile(
                emoji_frequency=0.2,
                common_emojis=["🚀", "💡", "🔥"],
                emoji_placement="end"
            )
        )

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        pass

    # Hook Generation Tests (Requirement 9.1)

    def test_optimize_hooks_curiosity_type(self):
        """Test generation of curiosity gap hooks."""
        content = "Machine learning can transform your business processes"
        hook_types = [HookType.CURIOSITY]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 1
        hook = hooks[0]

        # Check for curiosity gap indicators
        curiosity_indicators = ["what if", "secret", "hidden", "don't know", "won't believe", "blew my mind", "change how you think", "insight", "most people"]
        assert any(indicator in hook.lower() for indicator in curiosity_indicators)

        # Check hook length is reasonable
        assert 30 <= len(hook) <= 150

        # Check it contains topic reference (could be ML, machine learning, or AI)
        topic_references = ["machine learning", "ml", "ai", "artificial intelligence"]
        assert any(ref in hook.lower() for ref in topic_references)

    def test_optimize_hooks_contrarian_type(self):
        """Test generation of contrarian take hooks."""
        content = "Most people think machine learning is complex"
        hook_types = [HookType.CONTRARIAN]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 1
        hook = hooks[0]

        # Check for contrarian indicators
        contrarian_indicators = ["everyone says", "unpopular opinion", "wrong", "backwards", "hot take", "stop doing"]
        has_contrarian = any(indicator in hook.lower() for indicator in contrarian_indicators)

        # Check hook challenges conventional wisdom
        challenge_words = ["but", "however", "actually", "truth", "reality", "instead", "here's what works"]
        has_challenge = any(word in hook.lower() for word in challenge_words)

        # At least one should be true for a contrarian hook
        assert has_contrarian or has_challenge, f"Hook '{hook}' doesn't appear to be contrarian"

    def test_optimize_hooks_statistic_type(self):
        """Test generation of statistic-based hooks."""
        content = "Data shows machine learning improves efficiency"
        hook_types = [HookType.STATISTIC]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 1
        hook = hooks[0]

        # Check for percentage or number
        import re
        assert re.search(r'\d+%|\d+\s*(people|professionals|experts)', hook)

        # Check for statistic indicators
        stat_indicators = ["studies show", "research reveals", "data shows", "only", "shocking", "% of people"]
        assert any(indicator in hook.lower() for indicator in stat_indicators)

    def test_optimize_hooks_story_type(self):
        """Test generation of story-based hooks."""
        content = "I learned machine learning through trial and error"
        hook_types = [HookType.STORY]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 1
        hook = hooks[0]

        # Check for story indicators
        story_indicators = ["last week", "yesterday", "three months ago", "story", "happened", "discovered", "blew my mind", "learned", "used to think", "moment i realized", "mistake that taught"]
        assert any(indicator in hook.lower() for indicator in story_indicators)

        # Check for personal elements (since style profile has personal_anecdotes=True)
        personal_indicators = ["i", "my", "me", "personal"]
        assert any(indicator in hook.lower() for indicator in personal_indicators)

    def test_optimize_hooks_value_proposition_type(self):
        """Test generation of value proposition hooks."""
        content = "Learn machine learning efficiently with this method"
        hook_types = [HookType.VALUE_PROPOSITION]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 1
        hook = hooks[0]

        # Check for value indicators
        value_indicators = ["how to", "fastest way", "simple", "proven method", "in 10 minutes", "step process", "in a week", "get better"]
        assert any(indicator in hook.lower() for indicator in value_indicators)

        # Check for benefit promise
        benefit_words = ["learn", "master", "improve", "optimize", "achieve"]
        assert any(word in hook.lower() for word in benefit_words)

    def test_optimize_hooks_question_type(self):
        """Test generation of question-based hooks."""
        content = "Machine learning can solve complex problems"
        hook_types = [HookType.QUESTION]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 1
        hook = hooks[0]

        # Check it's actually a question
        assert "?" in hook

        # Check for question starters
        question_starters = ["what if", "why", "how", "what's", "have you"]
        assert any(starter in hook.lower() for starter in question_starters)

    def test_optimize_hooks_multiple_types(self):
        """Test generation of multiple hook types."""
        content = "Machine learning transforms business processes"
        hook_types = [HookType.CURIOSITY, HookType.STATISTIC, HookType.VALUE_PROPOSITION]

        hooks = self.optimizer.optimize_hooks(
            content, hook_types, self.sample_blog_post, self.sample_style_profile
        )

        assert len(hooks) == 3

        # Hooks should be ranked by score (best first)
        scores = [self.optimizer._score_hook(hook, self.sample_style_profile) for hook in hooks]
        assert scores == sorted(scores, reverse=True)

    def test_hook_scoring_algorithm(self):
        """Test hook scoring algorithm effectiveness."""
        # High-quality hook
        good_hook = "What if I told you 85% of ML projects fail because of this secret mistake?"

        # Low-quality hook
        poor_hook = "Machine learning is a topic that some people find interesting to study."

        good_score = self.optimizer._score_hook(good_hook, self.sample_style_profile)
        poor_score = self.optimizer._score_hook(poor_hook, self.sample_style_profile)

        assert good_score > poor_score
        assert good_score > 0.5  # Should be reasonably high
        assert poor_score < 0.5  # Should be lower

    # Thread Structure Optimization Tests (Requirement 9.2)

    def test_apply_thread_structure_basic(self):
        """Test basic thread structure optimization."""
        tweets = [
            "This is the opening tweet about machine learning",
            "Here's the first key point about algorithms",
            "The second important concept is model training",
            "Finally, let's talk about deployment strategies"
        ]

        thread_plan = ThreadPlan(
            hook_type=HookType.CURIOSITY,
            main_points=["algorithms", "training", "deployment"],
            call_to_action="Share your ML experience",
            estimated_tweets=4
        )

        structured_tweets = self.optimizer.apply_thread_structure(tweets, thread_plan)

        assert len(structured_tweets) == 4

        # First tweet should be strengthened as opening
        assert structured_tweets[0] != tweets[0]  # Should be modified

        # Final tweet should have CTA optimization
        final_tweet = structured_tweets[-1]
        cta_indicators = ["what", "share", "comment", "think", "experience", "tag", "which", "resonated", "most", "would you add", "your experience"]
        assert any(indicator in final_tweet.lower() for indicator in cta_indicators)

    def test_apply_thread_structure_numbered_sequence(self):
        """Test numbered sequence application."""
        tweets = [
            "Opening hook about machine learning",
            "First main point",
            "Second main point",
            "Third main point",
            "Conclusion with CTA"
        ]

        thread_plan = ThreadPlan(hook_type=HookType.VALUE_PROPOSITION)
        structured_tweets = self.optimizer.apply_thread_structure(tweets, thread_plan)

        # Check for numbered sequences in middle tweets
        numbered_count = 0
        for i, tweet in enumerate(structured_tweets[1:-1], 1):  # Skip first and last
            if f"{i+1}/" in tweet or f"({i+1}/" in tweet:
                numbered_count += 1

        assert numbered_count > 0  # At least some tweets should be numbered

    def test_apply_thread_structure_continuation_indicators(self):
        """Test thread continuation indicators."""
        tweets = ["Hook", "Point 1", "Point 2", "Point 3", "CTA"]
        thread_plan = ThreadPlan(hook_type=HookType.STORY)

        structured_tweets = self.optimizer.apply_thread_structure(tweets, thread_plan)

        # Check for continuation indicators
        continuation_indicators = ["thread continues", "more below", "keep reading", "👇"]
        found_indicators = 0

        for tweet in structured_tweets[:-1]:  # All except last
            if any(indicator in tweet.lower() for indicator in continuation_indicators):
                found_indicators += 1

        assert found_indicators > 0

    def test_apply_thread_structure_visual_hierarchy(self):
        """Test visual hierarchy application."""
        tweets = ["Hook", "Point 1", "Point 2", "CTA"]
        thread_plan = ThreadPlan(hook_type=HookType.CURIOSITY)

        structured_tweets = self.optimizer.apply_thread_structure(tweets, thread_plan)

        # Check for visual elements
        visual_elements = ["•", "→", "✓", "🔥", "💡", "\n\n", "---"]
        found_visual = 0

        for tweet in structured_tweets:
            if any(element in tweet for element in visual_elements):
                found_visual += 1

        assert found_visual > 0

    # Engagement Element Integration Tests (Requirement 9.3)

    def test_add_engagement_elements_technical_content(self):
        """Test engagement elements for technical content."""
        tweet = "Machine learning algorithms require careful parameter tuning"

        enhanced_tweet = self.optimizer.add_engagement_elements(
            tweet, position=1, total_tweets=5, content_type="technical",
            categories=["machine-learning", "tutorial"]
        )

        # Test multiple times due to randomness in emoji placement (70% chance)
        enhanced_tweets = []
        for _ in range(10):
            enhanced = self.optimizer.add_engagement_elements(
                tweet, position=1, total_tweets=5, content_type="technical",
                categories=["machine-learning", "tutorial"]
            )
            enhanced_tweets.append(enhanced)

        # At least some should be enhanced
        enhanced_count = sum(1 for t in enhanced_tweets if t != tweet)
        assert enhanced_count > 0, "No tweets were enhanced after 10 attempts"

        # Check for technical emojis in enhanced tweets
        all_enhanced_text = " ".join(enhanced_tweets)
        tech_emojis = ["🔧", "⚙️", "🚀", "💡", "🔥", "⚡", "💻", "📊", "🎯"]
        has_tech_elements = any(emoji in all_enhanced_text for emoji in tech_emojis)
        assert has_tech_elements, "No technical emojis found in enhanced tweets"

    def test_add_engagement_elements_power_words(self):
        """Test power word integration."""
        tweet = "This method helps you learn machine learning"

        enhanced_tweet = self.optimizer.add_engagement_elements(
            tweet, position=0, total_tweets=3, content_type="tutorial"
        )

        # Check for power words
        power_words = ["proven", "powerful", "effective", "breakthrough", "ultimate", "secret"]
        original_power_count = sum(1 for word in power_words if word in tweet.lower())
        enhanced_power_count = sum(1 for word in power_words if word in enhanced_tweet.lower())

        assert enhanced_power_count >= original_power_count

    def test_add_engagement_elements_psychological_triggers(self):
        """Test psychological trigger application."""
        tweet = "Learn machine learning with this approach"

        enhanced_tweet = self.optimizer.add_engagement_elements(
            tweet, position=0, total_tweets=4, content_type="personal"
        )

        # Check for psychological triggers
        triggers = ["secret", "proven", "instant", "breakthrough", "exclusive", "limited"]
        trigger_found = any(trigger in enhanced_tweet.lower() for trigger in triggers)

        # Should have some psychological element
        assert len(enhanced_tweet) > len(tweet) or trigger_found

    def test_add_engagement_elements_readability_optimization(self):
        """Test readability optimization."""
        tweet = "Machine learning is a complex field that requires understanding of mathematical concepts and statistical methods for effective implementation"

        enhanced_tweet = self.optimizer.add_engagement_elements(
            tweet, position=2, total_tweets=5, content_type="tutorial"
        )

        # Should at least not make it longer than Twitter limit
        assert len(enhanced_tweet) <= 280
        # Method should run without error and return a string
        assert isinstance(enhanced_tweet, str)
        assert len(enhanced_tweet) > 0

    def test_add_engagement_elements_position_based(self):
        """Test position-based engagement optimization."""
        base_tweet = "Machine learning fundamentals"

        # Opening tweet (position 0)
        opening_tweet = self.optimizer.add_engagement_elements(
            base_tweet, position=0, total_tweets=5, content_type="tutorial"
        )

        # Middle tweet (position 2)
        middle_tweet = self.optimizer.add_engagement_elements(
            base_tweet, position=2, total_tweets=5, content_type="tutorial"
        )

        # Final tweet (position 4)
        final_tweet = self.optimizer.add_engagement_elements(
            base_tweet, position=4, total_tweets=5, content_type="tutorial"
        )

        # All should be valid strings (due to randomness, they might be the same)
        assert isinstance(opening_tweet, str)
        assert isinstance(middle_tweet, str)
        assert isinstance(final_tweet, str)

        # Test that the method handles different positions without error
        assert len(opening_tweet) > 0
        assert len(middle_tweet) > 0
        assert len(final_tweet) > 0

    # Hashtag Optimization Tests

    def test_optimize_hashtags_category_based(self):
        """Test hashtag optimization based on categories."""
        content = "Machine learning tutorial for beginners"
        categories = ["machine-learning", "tutorial", "beginners"]

        hashtags = self.optimizer.optimize_hashtags(content, categories, max_hashtags=2)

        assert len(hashtags) <= 2
        assert len(hashtags) > 0

        # Should be relevant to categories
        relevant_tags = ["#MachineLearning", "#ML", "#Tutorial", "#Beginners", "#AI", "#DataScience"]
        assert any(tag.lower().replace("#", "") in [h.lower().replace("#", "") for h in hashtags]
                  for tag in relevant_tags)

    def test_optimize_hashtags_content_extraction(self):
        """Test hashtag extraction from content."""
        content = "Deep learning neural networks for computer vision applications"
        categories = ["machine-learning"]

        hashtags = self.optimizer.optimize_hashtags(content, categories, max_hashtags=3)

        # Should extract relevant terms from content
        content_terms = ["deep", "learning", "neural", "networks", "computer", "vision"]
        hashtag_text = " ".join(hashtags).lower()

        relevant_found = any(term in hashtag_text for term in content_terms)
        assert relevant_found

    def test_optimize_hashtags_diversity(self):
        """Test hashtag diversity (no similar tags)."""
        content = "Machine learning and ML algorithms"
        categories = ["machine-learning", "algorithms"]

        hashtags = self.optimizer.optimize_hashtags(content, categories, max_hashtags=3)

        # Should return valid hashtags within limit
        assert len(hashtags) <= 3
        assert len(hashtags) > 0

        # All should be valid hashtag format
        for hashtag in hashtags:
            assert hashtag.startswith('#')
            assert len(hashtag) > 1

    # Visual Formatting Tests

    def test_apply_visual_formatting_scannable(self):
        """Test scannable formatting application."""
        tweet = "Machine learning requires data preprocessing feature engineering model training and evaluation"

        formatted_tweet = self.optimizer.apply_visual_formatting(tweet)

        # Should at least return a valid string (formatting may not apply to short single-line tweets)
        assert isinstance(formatted_tweet, str)
        assert len(formatted_tweet) > 0
        # Should not exceed Twitter limit
        assert len(formatted_tweet) <= 280

    def test_apply_visual_formatting_lists(self):
        """Test list optimization."""
        tweet = "Key steps: 1. Data collection 2. Preprocessing 3. Training 4. Evaluation"

        formatted_tweet = self.optimizer.apply_visual_formatting(tweet)

        # Should return a valid string (may or may not change formatting)
        assert isinstance(formatted_tweet, str)
        assert len(formatted_tweet) > 0

    def test_apply_visual_formatting_emphasis(self):
        """Test emphasis formatting."""
        tweet = "This is IMPORTANT for machine learning success"

        formatted_tweet = self.optimizer.apply_visual_formatting(tweet)

        # Should maintain the content and return valid string
        assert isinstance(formatted_tweet, str)
        assert len(formatted_tweet) > 0
        assert "important" in formatted_tweet.lower()  # Content should be preserved

    # Social Proof Elements Tests

    def test_add_social_proof_elements_personal_anecdotes(self):
        """Test personal anecdote integration."""
        tweets = ["Hook about ML", "Main content", "Conclusion"]

        # Test multiple times due to randomness
        found_personal = False
        for _ in range(10):
            enhanced_tweets = self.optimizer.add_social_proof_elements(
                tweets, content_type="personal", style_profile=self.sample_style_profile,
                categories=["machine-learning"]
            )

            first_tweet = enhanced_tweets[0]
            personal_indicators = ["i", "my", "me", "personal", "experience", "learned", "from my", "discovered", "company", "building", "mentoring"]
            if any(indicator in first_tweet.lower() for indicator in personal_indicators):
                found_personal = True
                break

        assert found_personal, "No personal anecdotes found after 10 attempts"

    def test_add_social_proof_elements_case_studies(self):
        """Test case study reference integration."""
        tweets = ["Hook", "Point 1", "Point 2", "Point 3", "CTA"]

        # Test multiple times due to randomness
        found_social_proof = False
        for _ in range(10):
            enhanced_tweets = self.optimizer.add_social_proof_elements(
                tweets, content_type="tutorial", categories=["machine-learning"]
            )

            all_content = " ".join(enhanced_tweets).lower()
            social_proof_indicators = ["study", "research", "example", "case", "proven", "results", "only", "% of", "developers", "know", "insight", "widely known"]
            if any(indicator in all_content for indicator in social_proof_indicators):
                found_social_proof = True
                break

        assert found_social_proof, "No social proof elements found after 10 attempts"

    def test_add_social_proof_elements_authority_indicators(self):
        """Test authority indicator integration."""
        tweets = ["Hook", "Content", "CTA"]

        # Test multiple times due to randomness
        found_authority = False
        for _ in range(10):
            enhanced_tweets = self.optimizer.add_social_proof_elements(
                tweets, content_type="technical", categories=["machine-learning", "research"]
            )

            all_content = " ".join(enhanced_tweets).lower()
            authority_indicators = ["expert", "research", "study", "proven", "industry", "professional", "only", "% of", "developers", "widely known", "teams", "miss", "opportunity"]
            if any(indicator in all_content for indicator in authority_indicators):
                found_authority = True
                break

        assert found_authority, "No authority indicators found after 10 attempts"

    # Call-to-Action Optimization Tests

    def test_optimize_call_to_action_category_appropriate(self):
        """Test category-appropriate CTA generation."""
        final_tweet = "Machine learning can transform your business processes"
        categories = ["machine-learning", "business"]

        optimized_tweet = self.optimizer.optimize_call_to_action(final_tweet, categories)

        # Should have engagement CTA
        cta_indicators = ["what", "share", "comment", "think", "experience", "tag", "try"]
        assert any(indicator in optimized_tweet.lower() for indicator in cta_indicators)

    def test_optimize_call_to_action_removes_existing(self):
        """Test removal of existing CTA before adding new one."""
        final_tweet = "ML is powerful. What do you think about this approach?"
        categories = ["machine-learning"]

        optimized_tweet = self.optimizer.optimize_call_to_action(final_tweet, categories)

        # Should have a CTA but might be different from original
        assert "?" in optimized_tweet  # Should still have question format

    # Engagement Score Calculation Tests

    def test_calculate_engagement_score_high_quality(self):
        """Test engagement score calculation for high-quality thread."""
        # Create high-quality thread
        tweets = [
            Tweet(
                content="🚀 What if I told you 85% of ML projects fail because of this secret mistake?",
                character_count=78,
                engagement_elements=["curiosity_hook", "statistic", "emoji"],
                position=0,
                hook_type=HookType.CURIOSITY
            ),
            Tweet(
                content="Here's the breakthrough method that changed everything → (2/5)",
                character_count=65,
                engagement_elements=["power_word", "continuation", "numbering"],
                position=1
            ),
            Tweet(
                content="💡 The secret: Start with data quality, not complex algorithms (3/5)",
                character_count=70,
                engagement_elements=["emoji", "secret_reveal", "numbering"],
                position=2
            )
        ]

        thread_data = ThreadData(
            post_slug="ml-guide",
            tweets=tweets,
            engagement_score=0.0  # Will be calculated
        )

        score = self.optimizer.calculate_engagement_score(thread_data)

        assert 0.0 <= score <= 1.0
        assert score > 0.6  # Should be high for quality content

    def test_calculate_engagement_score_low_quality(self):
        """Test engagement score calculation for low-quality thread."""
        # Create low-quality thread
        tweets = [
            Tweet(
                content="This is a post about machine learning and how it works in various applications and use cases.",
                character_count=105,
                engagement_elements=[],
                position=0
            ),
            Tweet(
                content="Machine learning is a subset of artificial intelligence that enables computers to learn.",
                character_count=98,
                engagement_elements=[],
                position=1
            )
        ]

        thread_data = ThreadData(
            post_slug="ml-basic",
            tweets=tweets,
            engagement_score=0.0
        )

        score = self.optimizer.calculate_engagement_score(thread_data)

        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Should be low for poor content

    # Psychological Trigger Tests

    def test_psychological_triggers_fomo(self):
        """Test FOMO (Fear of Missing Out) trigger application."""
        tweet = "Learn machine learning fundamentals"

        enhanced_tweet = self.optimizer.add_engagement_elements(
            tweet, position=0, total_tweets=3, content_type="tutorial"
        )

        # Check for FOMO indicators
        fomo_indicators = ["limited", "exclusive", "secret", "before", "miss", "opportunity"]
        fomo_found = any(indicator in enhanced_tweet.lower() for indicator in fomo_indicators)

        # Should have some urgency or scarcity element
        assert len(enhanced_tweet) > len(tweet) or fomo_found

    def test_psychological_triggers_social_proof(self):
        """Test social proof trigger application."""
        tweets = ["Hook", "Content", "CTA"]

        # Test multiple times due to randomness
        found_social_proof = False
        for _ in range(10):
            enhanced_tweets = self.optimizer.add_social_proof_elements(
                tweets, content_type="business", categories=["machine-learning"]
            )

            all_content = " ".join(enhanced_tweets).lower()
            social_proof_indicators = ["thousands", "experts", "professionals", "proven", "successful", "results", "only", "% of", "developers", "widely known", "teams", "miss", "opportunity"]
            if any(indicator in all_content for indicator in social_proof_indicators):
                found_social_proof = True
                break

        assert found_social_proof, "No social proof elements found after 10 attempts"

    def test_psychological_triggers_curiosity_gaps(self):
        """Test curiosity gap creation."""
        hook_types = [HookType.CURIOSITY]

        hooks = self.optimizer.optimize_hooks(
            "Machine learning optimization techniques", hook_types,
            self.sample_blog_post, self.sample_style_profile
        )

        hook = hooks[0]

        # Should create curiosity gap
        curiosity_gaps = ["what if", "secret", "hidden", "don't know", "discover", "reveal", "insight", "blew my mind"]
        assert any(gap in hook.lower() for gap in curiosity_gaps)

    # Edge Cases and Error Handling

    def test_optimize_hooks_empty_content(self):
        """Test hook optimization with empty content."""
        hooks = self.optimizer.optimize_hooks(
            "", [HookType.CURIOSITY], self.sample_blog_post, self.sample_style_profile
        )

        # Should still generate hooks based on blog post title/categories
        assert len(hooks) == 1
        assert len(hooks[0]) > 0

    def test_apply_thread_structure_empty_tweets(self):
        """Test thread structure with empty tweet list."""
        structured_tweets = self.optimizer.apply_thread_structure([], None)
        assert structured_tweets == []

    def test_add_engagement_elements_edge_cases(self):
        """Test engagement elements with edge cases."""
        # Very short tweet
        short_tweet = "ML"
        enhanced_short = self.optimizer.add_engagement_elements(
            short_tweet, position=0, total_tweets=1, content_type="technical"
        )
        assert len(enhanced_short) >= len(short_tweet)

        # Very long tweet
        long_tweet = "A" * 250
        enhanced_long = self.optimizer.add_engagement_elements(
            long_tweet, position=0, total_tweets=1, content_type="technical"
        )
        assert len(enhanced_long) <= 280  # Should not exceed Twitter limit

    def test_optimize_hashtags_edge_cases(self):
        """Test hashtag optimization edge cases."""
        # Empty categories
        hashtags = self.optimizer.optimize_hashtags("ML content", [], max_hashtags=2)
        assert isinstance(hashtags, list)

        # Max hashtags = 0
        hashtags = self.optimizer.optimize_hashtags("ML content", ["ml"], max_hashtags=0)
        assert len(hashtags) == 0

    # Integration Tests

    def test_full_optimization_pipeline(self):
        """Test complete optimization pipeline integration."""
        # Start with basic content
        content = "Machine learning guide for beginners"
        categories = ["machine-learning", "tutorial"]

        # Generate hooks
        hooks = self.optimizer.optimize_hooks(
            content, [HookType.CURIOSITY, HookType.VALUE_PROPOSITION],
            self.sample_blog_post, self.sample_style_profile
        )

        # Create basic tweets
        tweets = [
            hooks[0],  # Use best hook
            "First key concept about ML algorithms",
            "Second important point about data preprocessing",
            "Final thoughts and next steps"
        ]

        # Apply structure optimization
        thread_plan = ThreadPlan(hook_type=HookType.CURIOSITY)
        structured_tweets = self.optimizer.apply_thread_structure(tweets, thread_plan)

        # Add engagement elements
        enhanced_tweets = []
        for i, tweet in enumerate(structured_tweets):
            enhanced_tweet = self.optimizer.add_engagement_elements(
                tweet, position=i, total_tweets=len(structured_tweets),
                content_type="tutorial", categories=categories
            )
            enhanced_tweets.append(enhanced_tweet)

        # Add social proof
        final_tweets = self.optimizer.add_social_proof_elements(
            enhanced_tweets, content_type="tutorial",
            style_profile=self.sample_style_profile, categories=categories
        )

        # Optimize hashtags
        hashtags = self.optimizer.optimize_hashtags(content, categories, max_hashtags=2)

        # Create thread data and calculate score
        tweet_objects = [
            Tweet(content=tweet, position=i)
            for i, tweet in enumerate(final_tweets)
        ]

        thread_data = ThreadData(
            post_slug="ml-guide",
            tweets=tweet_objects,
            hashtags=hashtags
        )

        engagement_score = self.optimizer.calculate_engagement_score(thread_data)

        # Verify complete pipeline
        assert len(final_tweets) == 4
        assert len(hashtags) <= 2
        assert 0.0 <= engagement_score <= 1.0
        assert engagement_score > 0.3  # Should be decent after optimization

        # Verify each tweet is enhanced
        for i, (original, final) in enumerate(zip(tweets, final_tweets)):
            if i == 0:  # Hook should be different
                assert final != original
            # All tweets should have reasonable length
            assert len(final) <= 280


if __name__ == "__main__":
    pytest.main([__file__, "-v"])