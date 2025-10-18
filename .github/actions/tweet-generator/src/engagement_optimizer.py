"""
Engagement optimization for the Tweet Thread Generator.

This module applies proven social media engagement techniques and optimization
strategies to maximize thread performance and audience interaction.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import random
from collections import Counter

from models import Tweet, ThreadData, HookType, StyleProfile, BlogPost
from exceptions import ValidationError
from utils import extract_hashtags


class EngagementOptimizer:
    """Optimizes tweet threads for maximum engagement."""

    def __init__(self, optimization_level: str = "high"):
        """
        Initialize engagement optimizer.

        Args:
            optimization_level: Level of optimization (low, medium, high)
        """
        self.optimization_level = optimization_level

    def optimize_hooks(self, content: str, hook_types: List[HookType],
                      blog_post: BlogPost, style_profile: Optional[StyleProfile] = None) -> List[str]:
        """
        Generate optimized hooks for thread opening.

        Args:
            content: Source content to create hooks from
            hook_types: Types of hooks to generate
            blog_post: Blog post data for context
            style_profile: Author's writing style profile

        Returns:
            List of optimized hook variations
        """
        hooks = []

        for hook_type in hook_types:
            hook = self._generate_hook_by_type(hook_type, content, blog_post, style_profile)
            if hook:
                hooks.append(hook)

        # Score and rank hooks
        scored_hooks = [(hook, self._score_hook(hook, style_profile)) for hook in hooks]
        scored_hooks.sort(key=lambda x: x[1], reverse=True)

        return [hook for hook, _ in scored_hooks]

    def apply_thread_structure(self, tweets: List[str], thread_plan: Any) -> List[str]:
        """
        Apply optimal thread structure and flow.

        Args:
            tweets: List of tweet content
            thread_plan: Thread structure plan

        Returns:
            List of structurally optimized tweets
        """
        if not tweets:
            return tweets

        structured_tweets = []

        for i, tweet in enumerate(tweets):
            # Apply thread arc pattern
            structured_tweet = self._apply_thread_arc_pattern(tweet, i, len(tweets))

            # Add numbered sequences with cliffhangers
            structured_tweet = self._add_numbered_sequence(structured_tweet, i, len(tweets))

            # Add thread continuation indicators
            structured_tweet = self._add_continuation_indicators(structured_tweet, i, len(tweets))

            # Apply visual hierarchy
            structured_tweet = self._apply_visual_hierarchy(structured_tweet, i, len(tweets))

            structured_tweets.append(structured_tweet)

        # Optimize final tweet with CTA
        if structured_tweets:
            structured_tweets[-1] = self._optimize_final_tweet_cta(structured_tweets[-1])

        return structured_tweets

    def add_engagement_elements(self, tweet: str, position: int, total_tweets: int,
                              content_type: str = "general", categories: List[str] = None) -> str:
        """
        Add engagement elements to individual tweets.

        Args:
            tweet: Tweet content
            position: Position in thread (0-based)
            total_tweets: Total number of tweets in thread
            content_type: Type of content (technical, personal, tutorial, etc.)
            categories: Content categories for context

        Returns:
            Tweet with engagement elements added
        """
        if categories is None:
            categories = []

        # Add strategic emoji placement
        tweet = self._add_strategic_emojis(tweet, position, total_tweets, content_type)

        # Integrate power words
        tweet = self._integrate_power_words(tweet, content_type)

        # Apply psychological triggers
        tweet = self._apply_psychological_triggers(tweet, position, total_tweets)

        # Optimize readability
        tweet = self._optimize_readability(tweet)

        return tweet

    def optimize_hashtags(self, content: str, categories: List[str], max_hashtags: int = 2) -> List[str]:
        """
        Select and optimize hashtags for maximum reach.

        Args:
            content: Tweet content
            categories: Content categories
            max_hashtags: Maximum number of hashtags

        Returns:
            List of optimized hashtags
        """
        hashtags = []

        # Get category-based hashtags
        category_hashtags = self._get_category_hashtags(categories)

        # Get content-based hashtags
        content_hashtags = self._extract_content_hashtags(content)

        # Get trending/popular hashtags for categories
        trending_hashtags = self._get_trending_hashtags(categories)

        # Combine and score hashtags
        all_hashtags = category_hashtags + content_hashtags + trending_hashtags
        scored_hashtags = [(tag, self._score_hashtag(tag, content, categories)) for tag in all_hashtags]

        # Sort by score and select top hashtags
        scored_hashtags.sort(key=lambda x: x[1], reverse=True)

        # Select diverse hashtags (avoid duplicates and similar tags)
        selected = []
        for hashtag, score in scored_hashtags:
            if len(selected) >= max_hashtags:
                break
            if not self._is_similar_hashtag(hashtag, selected):
                selected.append(hashtag)

        return selected

    def apply_visual_formatting(self, tweet: str) -> str:
        """
        Apply visual hierarchy and formatting techniques.

        Args:
            tweet: Tweet content to format

        Returns:
            Visually optimized tweet
        """
        # Apply scannable formatting
        tweet = self._make_scannable(tweet)

        # Add visual separators
        tweet = self._add_visual_separators(tweet)

        # Optimize bullet points and lists
        tweet = self._optimize_lists(tweet)

        # Apply emphasis formatting
        tweet = self._apply_emphasis_formatting(tweet)

        return tweet

    def add_social_proof_elements(self, tweets: List[str], content_type: str,
                                 style_profile: Optional[StyleProfile] = None,
                                 categories: List[str] = None) -> List[str]:
        """
        Add social proof and credibility elements.

        Args:
            tweets: List of tweet content
            content_type: Type of content (tutorial, personal, etc.)
            style_profile: Author's writing style profile for personal anecdotes
            categories: Content categories for context

        Returns:
            Tweets with social proof elements
        """
        if categories is None:
            categories = []

        enhanced_tweets = []

        for i, tweet in enumerate(tweets):
            enhanced_tweet = tweet

            # Add personal anecdotes (from style profile)
            if i == 0 and style_profile and style_profile.tone_indicators.personal_anecdotes:
                enhanced_tweet = self._add_personal_anecdote(enhanced_tweet, content_type)

            # Add case study references
            if i == len(tweets) // 2:  # Middle of thread
                enhanced_tweet = self._add_case_study_reference(enhanced_tweet, categories)

            # Add credible sources and authority indicators
            enhanced_tweet = self._add_authority_indicators(enhanced_tweet, categories, i, len(tweets))

            # Add urgency and scarcity triggers
            enhanced_tweet = self._add_urgency_scarcity(enhanced_tweet, i, len(tweets))

            # Add relatability factors
            enhanced_tweet = self._add_relatability_factors(enhanced_tweet, content_type, categories)

            enhanced_tweets.append(enhanced_tweet)

        return enhanced_tweets

    def optimize_call_to_action(self, final_tweet: str, content_categories: List[str]) -> str:
        """
        Optimize call-to-action for maximum engagement.

        Args:
            final_tweet: Final tweet in thread
            content_categories: Content categories for context

        Returns:
            Optimized final tweet with CTA
        """
        # Remove existing CTA if present
        tweet_without_cta = self._remove_existing_cta(final_tweet)

        # Generate category-appropriate CTA
        cta = self._generate_category_cta(content_categories)

        # Combine with proper formatting
        optimized_tweet = self._combine_tweet_with_cta(tweet_without_cta, cta)

        return optimized_tweet

    def calculate_engagement_score(self, thread_data: ThreadData) -> float:
        """
        Calculate predicted engagement score for thread.

        Args:
            thread_data: Complete thread data

        Returns:
            Engagement score (0.0 to 1.0)
        """
        score = 0.0
        total_factors = 0

        # Hook quality (30% of score)
        if thread_data.tweets:
            first_tweet = thread_data.tweets[0]
            hook_score = self._score_hook(first_tweet.content)
            score += hook_score * 0.3
            total_factors += 0.3

        # Thread structure (25% of score)
        structure_score = self._score_thread_structure(thread_data.tweets)
        score += structure_score * 0.25
        total_factors += 0.25

        # Engagement elements (25% of score)
        engagement_score = self._score_engagement_elements(thread_data.tweets)
        score += engagement_score * 0.25
        total_factors += 0.25

        # Character optimization (20% of score)
        char_score = self._score_character_optimization(thread_data.tweets)
        score += char_score * 0.2
        total_factors += 0.2

        return min(1.0, score / total_factors if total_factors > 0 else 0.0)

    def _generate_hook_by_type(self, hook_type: HookType, content: str,
                              blog_post: BlogPost, style_profile: Optional[StyleProfile] = None) -> str:
        """Generate a hook based on the specified type."""
        title = blog_post.title
        categories = blog_post.categories

        if hook_type == HookType.CURIOSITY:
            return self._generate_curiosity_hook(title, content, categories)
        elif hook_type == HookType.CONTRARIAN:
            return self._generate_contrarian_hook(title, content, categories)
        elif hook_type == HookType.STATISTIC:
            return self._generate_statistic_hook(title, content, categories)
        elif hook_type == HookType.STORY:
            return self._generate_story_hook(title, content, categories, style_profile)
        elif hook_type == HookType.VALUE_PROPOSITION:
            return self._generate_value_proposition_hook(title, content, categories)
        elif hook_type == HookType.QUESTION:
            return self._generate_question_hook(title, content, categories)

        return ""

    def _generate_curiosity_hook(self, title: str, content: str, categories: List[str]) -> str:
        """Generate curiosity gap hooks."""
        curiosity_templates = [
            "What if I told you {topic}?",
            "The secret that {industry} doesn't want you to know:",
            "Here's something that will change how you think about {topic}:",
            "Most people don't know this about {topic}:",
            "The hidden truth behind {topic}:",
            "You won't believe what I discovered about {topic}:",
            "This {topic} insight blew my mind:",
            "The one thing about {topic} that everyone gets wrong:"
        ]

        # Extract key topic from title
        topic = self._extract_main_topic(title, categories)
        industry = self._get_industry_context(categories)

        template = random.choice(curiosity_templates)
        return template.format(topic=topic, industry=industry)

    def _generate_contrarian_hook(self, title: str, content: str, categories: List[str]) -> str:
        """Generate contrarian take hooks."""
        contrarian_templates = [
            "Everyone says {common_belief}, but here's why they're wrong:",
            "Unpopular opinion: {contrarian_view}",
            "Stop doing {common_practice}. Here's what works instead:",
            "The {industry} advice everyone follows is backwards:",
            "Why everything you know about {topic} is wrong:",
            "Hot take: {contrarian_statement}",
            "Controversial truth: {topic} isn't what you think:",
            "I'm about to challenge everything you believe about {topic}:"
        ]

        topic = self._extract_main_topic(title, categories)
        industry = self._get_industry_context(categories)

        # Generate contrarian elements based on content
        common_belief = f"you need to {self._extract_common_approach(content)}"
        contrarian_view = f"{topic} is simpler than most people think"
        common_practice = self._extract_common_practice(content, categories)
        contrarian_statement = f"{topic} success comes from doing less, not more"

        template = random.choice(contrarian_templates)
        return template.format(
            topic=topic,
            industry=industry,
            common_belief=common_belief,
            contrarian_view=contrarian_view,
            common_practice=common_practice,
            contrarian_statement=contrarian_statement
        )

    def _generate_statistic_hook(self, title: str, content: str, categories: List[str]) -> str:
        """Generate statistic-based hooks."""
        statistic_templates = [
            "{percentage}% of people don't know this {topic} secret:",
            "Only {percentage}% of {professionals} do this correctly:",
            "Studies show {percentage}% of {topic} attempts fail because:",
            "{percentage}% of {industry} experts agree on this:",
            "Research reveals {percentage}% of people make this {topic} mistake:",
            "Shocking: {percentage}% of {professionals} ignore this {topic} rule:",
            "Data shows {percentage}% improvement when you:",
            "{percentage}% of successful {professionals} do this one thing:"
        ]

        topic = self._extract_main_topic(title, categories)
        industry = self._get_industry_context(categories)
        professionals = self._get_professional_context(categories)

        # Generate realistic percentages
        percentages = [73, 85, 92, 67, 78, 89, 94, 76, 82, 91]
        percentage = random.choice(percentages)

        template = random.choice(statistic_templates)
        return template.format(
            percentage=percentage,
            topic=topic,
            industry=industry,
            professionals=professionals
        )

    def _generate_story_hook(self, title: str, content: str, categories: List[str],
                           style_profile: Optional[StyleProfile] = None) -> str:
        """Generate story-based hooks."""
        story_templates = [
            "Last week something happened that changed everything I knew about {topic}:",
            "Three months ago, I made a {topic} mistake that taught me this:",
            "Yesterday I discovered something about {topic} that blew my mind:",
            "A conversation with a {professional} completely changed my view on {topic}:",
            "I used to think {topic} was {assumption}, until this happened:",
            "The moment I realized I was doing {topic} all wrong:",
            "A simple {topic} experiment led to an unexpected discovery:",
            "Here's the story of how I learned {topic} the hard way:"
        ]

        topic = self._extract_main_topic(title, categories)
        professional = self._get_professional_context(categories).rstrip('s')  # singular
        assumption = "complicated" if "technical" in categories else "simple"

        # Use personal anecdotes if available in style profile
        if style_profile and style_profile.tone_indicators.personal_anecdotes:
            personal_templates = [
                "Personal story: How {topic} changed my perspective:",
                "I'll never forget the day I learned this about {topic}:",
                "True story: My biggest {topic} breakthrough came from:",
                "Here's what happened when I tried {topic} differently:"
            ]
            story_templates.extend(personal_templates)

        template = random.choice(story_templates)
        return template.format(
            topic=topic,
            professional=professional,
            assumption=assumption
        )

    def _generate_value_proposition_hook(self, title: str, content: str, categories: List[str]) -> str:
        """Generate value proposition hooks."""
        value_templates = [
            "Here's how to {action} in {timeframe}:",
            "The fastest way to {action}:",
            "How I {achieved_result} using this {topic} method:",
            "The {number}-step process that {benefit}:",
            "How to {action} without {common_obstacle}:",
            "The simple {topic} trick that {benefit}:",
            "How to get {result} from {topic} in {timeframe}:",
            "The proven method to {action} that actually works:"
        ]

        topic = self._extract_main_topic(title, categories)

        # Generate value proposition elements
        action = self._extract_action_from_content(content, topic)
        timeframes = ["10 minutes", "one day", "a week", "30 days", "one hour"]
        timeframe = random.choice(timeframes)

        numbers = ["3", "5", "7", "4", "6"]
        number = random.choice(numbers)

        benefit = f"improves your {topic} results"
        achieved_result = f"mastered {topic}"
        common_obstacle = self._extract_common_obstacle(categories)
        result = f"better {topic} outcomes"

        template = random.choice(value_templates)
        return template.format(
            action=action,
            timeframe=timeframe,
            topic=topic,
            number=number,
            benefit=benefit,
            achieved_result=achieved_result,
            common_obstacle=common_obstacle,
            result=result
        )

    def _generate_question_hook(self, title: str, content: str, categories: List[str]) -> str:
        """Generate question-based hooks."""
        question_templates = [
            "What if {scenario}?",
            "Why do most people struggle with {topic}?",
            "What's the biggest {topic} mistake you're making?",
            "How would your {outcome} change if {condition}?",
            "What if I told you {topic} could be {improvement}?",
            "Why isn't anyone talking about {topic}?",
            "What's stopping you from {goal}?",
            "How many times have you tried {action} and failed?"
        ]

        topic = self._extract_main_topic(title, categories)
        scenario = f"you could master {topic} in half the time"
        outcome = self._get_outcome_context(categories)
        condition = f"you approached {topic} differently"
        improvement = "10x easier"
        goal = f"achieving {topic} success"
        action = self._extract_action_from_content(content, topic)

        template = random.choice(question_templates)
        return template.format(
            scenario=scenario,
            topic=topic,
            outcome=outcome,
            condition=condition,
            improvement=improvement,
            goal=goal,
            action=action
        )

    def _score_hook(self, hook: str, style_profile: Optional[StyleProfile] = None) -> float:
        """Score a hook based on engagement potential."""
        score = 0.0

        # Length optimization (ideal 50-100 characters)
        length = len(hook)
        if 50 <= length <= 100:
            score += 0.3
        elif 40 <= length <= 120:
            score += 0.2
        else:
            score += 0.1

        # Power words
        power_words = [
            "secret", "proven", "breakthrough", "instant", "ultimate", "hidden",
            "shocking", "amazing", "incredible", "powerful", "simple", "easy",
            "fast", "quick", "effective", "guaranteed", "exclusive", "free"
        ]
        power_word_count = sum(1 for word in power_words if word.lower() in hook.lower())
        score += min(0.2, power_word_count * 0.1)

        # Psychological triggers
        triggers = [
            "what if", "secret", "mistake", "wrong", "truth", "hidden",
            "don't know", "won't believe", "change", "discover", "reveal"
        ]
        trigger_count = sum(1 for trigger in triggers if trigger.lower() in hook.lower())
        score += min(0.2, trigger_count * 0.1)

        # Question or curiosity gap
        if "?" in hook or any(word in hook.lower() for word in ["what", "why", "how", "when"]):
            score += 0.15

        # Numbers and statistics
        if re.search(r'\d+%|\d+\s*(steps?|ways?|methods?|tips?)', hook):
            score += 0.15

        # Style profile alignment
        if style_profile:
            # Match formality level
            formality = style_profile.tone_indicators.formality_level
            if formality < 0.3 and any(word in hook.lower() for word in ["here's", "you'll", "i'll"]):
                score += 0.1
            elif formality > 0.7 and not any(word in hook.lower() for word in ["here's", "you'll", "gonna"]):
                score += 0.1

        return min(1.0, score)

    def _extract_main_topic(self, title: str, categories: List[str]) -> str:
        """Extract the main topic from title and categories."""
        # Remove common words and extract key terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        title_words = [word.lower() for word in title.split() if word.lower() not in stop_words]

        # Use categories as context
        if categories:
            primary_category = categories[0].replace("-", " ").replace("_", " ")
            return primary_category

        # Extract from title
        if title_words:
            return " ".join(title_words[:2])  # First two meaningful words

        return "this topic"

    def _get_industry_context(self, categories: List[str]) -> str:
        """Get industry context from categories."""
        industry_mapping = {
            "programming": "tech industry",
            "data-science": "data science field",
            "machine-learning": "AI industry",
            "web-development": "web development",
            "tutorial": "education sector",
            "career": "professional world",
            "business": "business world",
            "finance": "finance industry",
            "marketing": "marketing industry"
        }

        for category in categories:
            if category in industry_mapping:
                return industry_mapping[category]

        return "industry"

    def _get_professional_context(self, categories: List[str]) -> str:
        """Get professional context from categories."""
        professional_mapping = {
            "programming": "developers",
            "data-science": "data scientists",
            "machine-learning": "ML engineers",
            "web-development": "web developers",
            "tutorial": "learners",
            "career": "professionals",
            "business": "entrepreneurs",
            "finance": "analysts",
            "marketing": "marketers"
        }

        for category in categories:
            if category in professional_mapping:
                return professional_mapping[category]

        return "professionals"

    def _get_outcome_context(self, categories: List[str]) -> str:
        """Get outcome context from categories."""
        outcome_mapping = {
            "programming": "code quality",
            "data-science": "analysis results",
            "machine-learning": "model performance",
            "web-development": "website performance",
            "tutorial": "learning outcomes",
            "career": "career growth",
            "business": "business results",
            "finance": "financial returns",
            "marketing": "campaign results"
        }

        for category in categories:
            if category in outcome_mapping:
                return outcome_mapping[category]

        return "results"

    def _extract_common_approach(self, content: str) -> str:
        """Extract common approach mentioned in content."""
        # Look for patterns like "most people", "typically", "usually"
        approaches = [
            "follow tutorials blindly",
            "copy-paste solutions",
            "skip the fundamentals",
            "rush through the process",
            "ignore best practices"
        ]
        return random.choice(approaches)

    def _extract_common_practice(self, content: str, categories: List[str]) -> str:
        """Extract common practice from content and categories."""
        practice_mapping = {
            "programming": "copying code without understanding",
            "data-science": "jumping straight to modeling",
            "machine-learning": "using complex algorithms first",
            "web-development": "optimizing prematurely",
            "tutorial": "skipping the basics",
            "career": "networking only when job hunting",
            "business": "scaling too early"
        }

        for category in categories:
            if category in practice_mapping:
                return practice_mapping[category]

        return "following outdated advice"

    def _extract_action_from_content(self, content: str, topic: str) -> str:
        """Extract actionable verb from content."""
        actions = [
            f"master {topic}",
            f"improve your {topic}",
            f"learn {topic}",
            f"optimize {topic}",
            f"understand {topic}",
            f"implement {topic}",
            f"debug {topic}",
            f"scale {topic}"
        ]
        return random.choice(actions)

    def _extract_common_obstacle(self, categories: List[str]) -> str:
        """Extract common obstacles from categories."""
        obstacle_mapping = {
            "programming": "complex syntax",
            "data-science": "messy data",
            "machine-learning": "overfitting",
            "web-development": "browser compatibility",
            "tutorial": "information overload",
            "career": "networking anxiety",
            "business": "limited resources"
        }

        for category in categories:
            if category in obstacle_mapping:
                return obstacle_mapping[category]

        return "common pitfalls"

    def _score_thread_structure(self, tweets: List[Tweet]) -> float:
        """Score thread structure quality."""
        if not tweets:
            return 0.0

        score = 0.0

        # Check for numbered sequence
        numbered_count = sum(1 for tweet in tweets if re.search(r'^\d+/', tweet.content))
        if numbered_count > len(tweets) * 0.5:
            score += 0.3

        # Check for engagement elements
        engagement_elements = sum(len(tweet.engagement_elements) for tweet in tweets)
        if engagement_elements > 0:
            score += 0.3

        # Check for call-to-action in final tweet
        if tweets and any(word in tweets[-1].content.lower() for word in ["what", "share", "comment", "think", "experience"]):
            score += 0.4

        return min(1.0, score)

    def _score_engagement_elements(self, tweets: List[Tweet]) -> float:
        """Score engagement elements across tweets."""
        if not tweets:
            return 0.0

        total_elements = sum(len(tweet.engagement_elements) for tweet in tweets)
        avg_elements = total_elements / len(tweets)

        # Ideal is 2-3 engagement elements per tweet
        if 2 <= avg_elements <= 3:
            return 1.0
        elif 1 <= avg_elements <= 4:
            return 0.7
        else:
            return 0.3

    def _score_character_optimization(self, tweets: List[Tweet]) -> float:
        """Score character count optimization."""
        if not tweets:
            return 0.0

        scores = []
        for tweet in tweets:
            char_count = tweet.character_count
            # Ideal range: 200-260 characters (leaves room for retweets)
            if 200 <= char_count <= 260:
                scores.append(1.0)
            elif 180 <= char_count <= 280:
                scores.append(0.8)
            elif char_count < 180:
                scores.append(0.6)  # Too short
            else:
                scores.append(0.0)  # Too long

        return sum(scores) / len(scores) if scores else 0.0

    def _apply_thread_arc_pattern(self, tweet: str, position: int, total_tweets: int) -> str:
        """Apply thread arc pattern (strong opening, valuable content, compelling CTA)."""
        if position == 0:
            # Strong opening - ensure hook is compelling
            return self._strengthen_opening(tweet)
        elif position == total_tweets - 1:
            # Compelling conclusion - will be handled by CTA optimization
            return tweet
        else:
            # Valuable middle content - add value indicators
            return self._add_value_indicators(tweet, position, total_tweets)

    def _add_numbered_sequence(self, tweet: str, position: int, total_tweets: int) -> str:
        """Add numbered sequences with cliffhangers."""
        if total_tweets <= 1:
            return tweet

        # Add thread numbering
        thread_number = f"{position + 1}/{total_tweets}"

        # Add cliffhanger for middle tweets
        if 0 < position < total_tweets - 1:
            cliffhanger = self._generate_cliffhanger(position, total_tweets)
            if cliffhanger:
                tweet = f"{tweet}\n\n{cliffhanger}"

        # Format with thread number
        if not tweet.startswith(f"{position + 1}/"):
            tweet = f"{thread_number} {tweet}"

        return tweet

    def _add_continuation_indicators(self, tweet: str, position: int, total_tweets: int) -> str:
        """Add thread continuation indicators and engagement drivers."""
        if total_tweets <= 1:
            return tweet

        # Add continuation indicators for middle tweets
        if 0 < position < total_tweets - 2:
            continuations = [
                "\n\n👇 Thread continues...",
                "\n\n🧵 More below...",
                "\n\n⬇️ Keep reading...",
                "\n\n📖 Story continues...",
                "\n\n🔽 Next up..."
            ]
            continuation = random.choice(continuations)
            tweet = f"{tweet}{continuation}"

        # Add engagement drivers for penultimate tweet
        elif position == total_tweets - 2:
            drivers = [
                "\n\n🔥 The best part is coming up...",
                "\n\n💡 Wait until you see what's next...",
                "\n\n⚡ The final piece will surprise you...",
                "\n\n🎯 Here's where it gets interesting...",
                "\n\n🚀 The conclusion will blow your mind..."
            ]
            driver = random.choice(drivers)
            tweet = f"{tweet}{driver}"

        return tweet

    def _apply_visual_hierarchy(self, tweet: str, position: int, total_tweets: int) -> str:
        """Apply visual hierarchy with line breaks and formatting."""
        # Add strategic line breaks for readability
        tweet = self._add_strategic_line_breaks(tweet)

        # Add emphasis for key points
        tweet = self._add_text_emphasis(tweet)

        # Ensure proper spacing
        tweet = self._normalize_spacing(tweet)

        return tweet

    def _optimize_final_tweet_cta(self, final_tweet: str) -> str:
        """Optimize the final tweet with compelling call-to-action."""
        # Ensure the tweet ends with engagement
        if not self._has_engagement_ending(final_tweet):
            cta_options = [
                "\n\nWhat's your experience with this?",
                "\n\nWhat do you think? Share your thoughts below 👇",
                "\n\nHave you tried this approach? Let me know!",
                "\n\nWhich part resonated most with you?",
                "\n\nTag someone who needs to see this 🔥",
                "\n\nSave this thread for later 📌",
                "\n\nRetweet if this was helpful! 🙏",
                "\n\nWhat would you add to this list?"
            ]
            cta = random.choice(cta_options)
            final_tweet = f"{final_tweet}{cta}"

        return final_tweet

    def _strengthen_opening(self, tweet: str) -> str:
        """Strengthen the opening tweet for maximum impact."""
        # Ensure it starts with impact
        if not self._has_strong_opening(tweet):
            # Add emphasis if needed
            if not tweet.startswith(("🔥", "💡", "⚡", "🚀", "🎯")):
                impact_emojis = ["🔥", "💡", "⚡", "🚀", "🎯"]
                emoji = random.choice(impact_emojis)
                tweet = f"{emoji} {tweet}"

        return tweet

    def _add_value_indicators(self, tweet: str, position: int, total_tweets: int) -> str:
        """Add value indicators to middle content."""
        # Add value markers for key insights
        value_markers = [
            "💡 Key insight:",
            "🎯 Pro tip:",
            "⚡ Quick win:",
            "🔑 Important:",
            "💪 Action step:",
            "🧠 Remember:",
            "🚀 Bonus:",
            "⭐ Essential:"
        ]

        # Randomly add value markers to some tweets
        if random.random() < 0.3:  # 30% chance
            marker = random.choice(value_markers)
            # Only add if not already present
            if not any(m.split()[1].rstrip(':') in tweet for m in value_markers):
                tweet = f"{marker} {tweet}"

        return tweet

    def _generate_cliffhanger(self, position: int, total_tweets: int) -> str:
        """Generate cliffhanger for thread continuation."""
        cliffhangers = [
            "But here's the twist...",
            "But wait, there's more...",
            "Here's where it gets interesting...",
            "But the real magic happens next...",
            "The plot thickens...",
            "But here's what surprised me...",
            "The breakthrough came when...",
            "But then I discovered...",
            "Here's the game-changer...",
            "The turning point was..."
        ]

        # Use different cliffhangers based on position
        if position < total_tweets // 2:
            return random.choice(cliffhangers[:5])  # Early cliffhangers
        else:
            return random.choice(cliffhangers[5:])  # Later cliffhangers

    def _add_strategic_line_breaks(self, tweet: str) -> str:
        """Add strategic line breaks for better readability."""
        # Split long sentences
        sentences = tweet.split('. ')
        if len(sentences) > 1:
            # Add line breaks between sentences if tweet is long
            if len(tweet) > 150:
                tweet = '.\n\n'.join(sentences[:-1]) + '.' + sentences[-1] if sentences[-1] else '.\n\n'.join(sentences)

        # Add breaks before lists or bullet points
        tweet = re.sub(r'([.!?])\s*([•\-\*])', r'\1\n\n\2', tweet)

        return tweet

    def _add_text_emphasis(self, tweet: str) -> str:
        """Add text emphasis for key points."""
        # Emphasize important words (but don't overdo it)
        emphasis_words = [
            'important', 'crucial', 'essential', 'key', 'critical',
            'breakthrough', 'game-changer', 'secret', 'proven'
        ]

        for word in emphasis_words:
            # Only emphasize if not already emphasized
            pattern = rf'\b{word}\b'
            if re.search(pattern, tweet, re.IGNORECASE) and word.upper() not in tweet:
                tweet = re.sub(pattern, word.upper(), tweet, count=1, flags=re.IGNORECASE)
                break  # Only emphasize one word per tweet

        return tweet

    def _normalize_spacing(self, tweet: str) -> str:
        """Normalize spacing and formatting."""
        # Remove excessive line breaks
        tweet = re.sub(r'\n{3,}', '\n\n', tweet)

        # Remove trailing spaces
        tweet = '\n'.join(line.rstrip() for line in tweet.split('\n'))

        # Ensure single space after periods
        tweet = re.sub(r'\.  +', '. ', tweet)

        return tweet.strip()

    def _has_engagement_ending(self, tweet: str) -> bool:
        """Check if tweet has an engagement-driving ending."""
        engagement_patterns = [
            r'\?$',  # Ends with question
            r'👇$',  # Ends with down arrow
            r'🔥$',  # Ends with fire emoji
            r'thoughts?',  # Asks for thoughts
            r'experience',  # Mentions experience
            r'let me know',  # Direct ask
            r'what do you think',  # Opinion request
            r'share',  # Sharing request
            r'tag someone',  # Tagging request
        ]

        return any(re.search(pattern, tweet.lower()) for pattern in engagement_patterns)

    def _has_strong_opening(self, tweet: str) -> bool:
        """Check if tweet has a strong opening."""
        strong_openings = [
            r'^[🔥💡⚡🚀🎯]',  # Starts with impact emoji
            r'^(What if|Here\'s|The secret|Most people)',  # Strong opening phrases
            r'^\d+/',  # Numbered thread
            r'^(Hot take|Unpopular opinion|Truth bomb)',  # Attention grabbers
        ]

        return any(re.search(pattern, tweet) for pattern in strong_openings)

    def _remove_existing_cta(self, tweet: str) -> str:
        """Remove existing call-to-action from tweet."""
        cta_patterns = [
            r'\n\n.*[?!]$',  # Question or exclamation at end
            r'\n\n.*👇.*$',  # Down arrow patterns
            r'\n\n.*thoughts.*$',  # Thoughts requests
            r'\n\n.*share.*$',  # Share requests
        ]

        for pattern in cta_patterns:
            tweet = re.sub(pattern, '', tweet, flags=re.IGNORECASE)

        return tweet.strip()

    def _generate_category_cta(self, categories: List[str]) -> str:
        """Generate category-appropriate call-to-action."""
        category_ctas = {
            "programming": [
                "What's your favorite debugging technique?",
                "Share your coding horror stories below 👇",
                "Which programming concept took you longest to master?",
                "Tag a developer who needs to see this 🔥"
            ],
            "data-science": [
                "What's your go-to data visualization tool?",
                "Share your biggest data cleaning nightmare 📊",
                "Which ML algorithm do you use most often?",
                "Tag a data scientist who would find this useful 📈"
            ],
            "tutorial": [
                "Did this help clarify things for you?",
                "What topic should I cover next?",
                "Share this with someone learning 📚",
                "What's your biggest learning challenge?"
            ],
            "career": [
                "What's your best career advice?",
                "Share your career pivot story 💼",
                "Tag someone climbing the career ladder 🚀",
                "What skill has been most valuable in your career?"
            ],
            "business": [
                "What's your biggest business lesson?",
                "Share your entrepreneurship journey 💡",
                "Tag an entrepreneur who needs this 🚀",
                "What business advice would you add?"
            ]
        }

        # Find matching category
        for category in categories:
            if category in category_ctas:
                return random.choice(category_ctas[category])

        # Default CTAs
        default_ctas = [
            "What do you think about this?",
            "Share your experience below 👇",
            "Tag someone who needs to see this 🔥",
            "What would you add to this list?",
            "Save this thread for later 📌",
            "Retweet if this was helpful! 🙏"
        ]

        return random.choice(default_ctas)

    def _combine_tweet_with_cta(self, tweet: str, cta: str) -> str:
        """Combine tweet content with call-to-action."""
        # Ensure proper spacing
        if not tweet.endswith(('\n', '.')):
            tweet = f"{tweet}."

        return f"{tweet}\n\n{cta}"

    def _add_strategic_emojis(self, tweet: str, position: int, total_tweets: int, content_type: str) -> str:
        """Add strategic emoji placement based on content type and position."""
        # Define emoji sets by content type
        emoji_sets = {
            "technical": {
                "start": ["💻", "🔧", "⚙️", "🛠️", "🔬"],
                "middle": ["💡", "⚡", "🎯", "🔑", "📊"],
                "end": ["🚀", "✅", "🎉", "💪", "🔥"]
            },
            "tutorial": {
                "start": ["📚", "🎓", "📖", "🧠", "💡"],
                "middle": ["👉", "📝", "🔍", "⭐", "💯"],
                "end": ["🎯", "✨", "🚀", "💪", "🏆"]
            },
            "personal": {
                "start": ["💭", "🤔", "💡", "🌟", "✨"],
                "middle": ["❤️", "🙏", "💪", "🌱", "🔥"],
                "end": ["🚀", "💫", "🎉", "❤️", "🙌"]
            },
            "business": {
                "start": ["💼", "📈", "🎯", "💡", "🚀"],
                "middle": ["💰", "📊", "⚡", "🔑", "💪"],
                "end": ["🏆", "💯", "🚀", "📈", "✅"]
            }
        }

        # Get appropriate emoji set
        emojis = emoji_sets.get(content_type, emoji_sets["technical"])

        # Determine position type
        if position == 0:
            emoji_type = "start"
        elif position == total_tweets - 1:
            emoji_type = "end"
        else:
            emoji_type = "middle"

        # Add emoji if not already present and appropriate
        if not self._has_emoji(tweet) and random.random() < 0.7:  # 70% chance
            emoji = random.choice(emojis[emoji_type])

            # Strategic placement
            if position == 0:
                # Opening tweet - start with emoji
                tweet = f"{emoji} {tweet}"
            elif ":" in tweet or "!" in tweet:
                # Emphasize key points
                tweet = tweet.replace(":", f": {emoji}", 1)
            else:
                # End with emoji for middle/end tweets
                tweet = f"{tweet} {emoji}"

        return tweet

    def _integrate_power_words(self, tweet: str, content_type: str) -> str:
        """Integrate power words based on content type."""
        power_words_by_type = {
            "technical": {
                "breakthrough": ["game-changing", "revolutionary", "cutting-edge"],
                "secret": ["hidden technique", "insider method", "pro tip"],
                "proven": ["battle-tested", "production-ready", "industry-standard"],
                "instant": ["immediate", "real-time", "on-the-spot"]
            },
            "tutorial": {
                "simple": ["straightforward", "easy-to-follow", "step-by-step"],
                "effective": ["powerful", "results-driven", "high-impact"],
                "complete": ["comprehensive", "all-in-one", "end-to-end"],
                "beginner": ["newcomer-friendly", "zero-to-hero", "from-scratch"]
            },
            "business": {
                "profitable": ["revenue-generating", "money-making", "high-ROI"],
                "growth": ["scaling", "expansion", "breakthrough"],
                "strategy": ["game-plan", "blueprint", "roadmap"],
                "success": ["winning", "profitable", "thriving"]
            }
        }

        # Get power words for content type
        power_words = power_words_by_type.get(content_type, power_words_by_type["technical"])

        # Replace generic words with power words (sparingly)
        replacements_made = 0
        max_replacements = 1  # Don't overdo it

        for generic, alternatives in power_words.items():
            if replacements_made >= max_replacements:
                break

            if generic in tweet.lower() and random.random() < 0.3:  # 30% chance
                alternative = random.choice(alternatives)
                tweet = re.sub(rf'\b{generic}\b', alternative, tweet, count=1, flags=re.IGNORECASE)
                replacements_made += 1

        return tweet

    def _apply_psychological_triggers(self, tweet: str, position: int, total_tweets: int) -> str:
        """Apply psychological triggers (FOMO, curiosity, social proof)."""
        triggers = []

        # FOMO triggers
        if position < total_tweets - 1:  # Not the last tweet
            fomo_phrases = [
                "Don't miss this",
                "Most people overlook this",
                "This changes everything",
                "You can't afford to ignore this"
            ]
            if random.random() < 0.2:  # 20% chance
                triggers.append(random.choice(fomo_phrases))

        # Curiosity triggers
        curiosity_phrases = [
            "Here's the surprising part",
            "But wait, there's more",
            "The plot thickens",
            "This will surprise you"
        ]
        if random.random() < 0.15:  # 15% chance
            triggers.append(random.choice(curiosity_phrases))

        # Social proof triggers
        social_proof_phrases = [
            "Thousands of developers use this",
            "Industry experts recommend",
            "Top companies implement this",
            "Proven by countless teams"
        ]
        if random.random() < 0.1:  # 10% chance
            triggers.append(random.choice(social_proof_phrases))

        # Apply triggers (max 1 per tweet)
        if triggers and not self._has_psychological_trigger(tweet):
            trigger = triggers[0]  # Use first trigger
            # Insert trigger naturally
            if "." in tweet:
                sentences = tweet.split(". ")
                if len(sentences) > 1:
                    tweet = f"{sentences[0]}. {trigger}: {'. '.join(sentences[1:])}"

        return tweet

    def _optimize_readability(self, tweet: str) -> str:
        """Optimize readability with short sentences and active voice."""
        # Split overly long sentences
        sentences = re.split(r'[.!?]+', tweet)
        optimized_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Break down long sentences (>20 words)
            words = sentence.split()
            if len(words) > 20:
                # Find natural break points
                break_points = self._find_sentence_breaks(words)
                if break_points:
                    mid_point = break_points[0]
                    part1 = " ".join(words[:mid_point])
                    part2 = " ".join(words[mid_point:])
                    optimized_sentences.extend([part1, part2])
                else:
                    optimized_sentences.append(sentence)
            else:
                optimized_sentences.append(sentence)

        # Rejoin sentences
        tweet = ". ".join(optimized_sentences)

        # Convert passive to active voice (basic patterns)
        tweet = self._convert_passive_to_active(tweet)

        # Ensure scannable format
        tweet = self._ensure_scannable_format(tweet)

        return tweet

    def _get_category_hashtags(self, categories: List[str]) -> List[str]:
        """Get hashtags based on content categories."""
        category_hashtag_map = {
            "programming": ["#coding", "#programming", "#developer", "#tech", "#software"],
            "data-science": ["#datascience", "#analytics", "#machinelearning", "#python", "#data"],
            "web-development": ["#webdev", "#frontend", "#backend", "#javascript", "#css"],
            "tutorial": ["#tutorial", "#learning", "#howto", "#education", "#tips"],
            "career": ["#career", "#professional", "#growth", "#leadership", "#success"],
            "business": ["#business", "#entrepreneur", "#startup", "#growth", "#strategy"],
            "machine-learning": ["#machinelearning", "#AI", "#deeplearning", "#ML", "#artificialintelligence"],
            "finance": ["#finance", "#investing", "#money", "#fintech", "#economics"]
        }

        hashtags = []
        for category in categories:
            if category in category_hashtag_map:
                hashtags.extend(category_hashtag_map[category])

        return hashtags

    def _extract_content_hashtags(self, content: str) -> List[str]:
        """Extract relevant hashtags from content."""
        # Look for key technical terms and concepts
        tech_terms = {
            "python": "#python",
            "javascript": "#javascript",
            "react": "#reactjs",
            "node": "#nodejs",
            "docker": "#docker",
            "kubernetes": "#kubernetes",
            "aws": "#aws",
            "api": "#api",
            "database": "#database",
            "sql": "#sql",
            "git": "#git",
            "github": "#github"
        }

        hashtags = []
        content_lower = content.lower()

        for term, hashtag in tech_terms.items():
            if term in content_lower:
                hashtags.append(hashtag)

        return hashtags

    def _get_trending_hashtags(self, categories: List[str]) -> List[str]:
        """Get trending hashtags for categories."""
        # Simulated trending hashtags (in real implementation, this could use Twitter API)
        trending_by_category = {
            "programming": ["#100DaysOfCode", "#CodeNewbie", "#DevCommunity", "#TechTwitter"],
            "data-science": ["#DataScience", "#BigData", "#Analytics", "#DataViz"],
            "tutorial": ["#LearnInPublic", "#TechTips", "#DevTips", "#CodingTips"],
            "career": ["#TechCareers", "#CareerAdvice", "#ProfessionalGrowth", "#Leadership"],
            "business": ["#TechStartup", "#Innovation", "#DigitalTransformation", "#Entrepreneurship"]
        }

        hashtags = []
        for category in categories:
            if category in trending_by_category:
                hashtags.extend(trending_by_category[category])

        return hashtags

    def _score_hashtag(self, hashtag: str, content: str, categories: List[str]) -> float:
        """Score hashtag relevance and effectiveness."""
        score = 0.0

        # Relevance to content
        hashtag_clean = hashtag.lower().replace("#", "")
        if hashtag_clean in content.lower():
            score += 0.4

        # Category alignment
        for category in categories:
            if category.replace("-", "").replace("_", "") in hashtag_clean:
                score += 0.3

        # Hashtag popularity (simulated)
        popular_hashtags = [
            "#programming", "#coding", "#developer", "#tech", "#datascience",
            "#webdev", "#javascript", "#python", "#machinelearning", "#AI"
        ]
        if hashtag in popular_hashtags:
            score += 0.2

        # Length preference (shorter is better)
        if len(hashtag) <= 15:
            score += 0.1

        return min(1.0, score)

    def _is_similar_hashtag(self, hashtag: str, selected: List[str]) -> bool:
        """Check if hashtag is too similar to already selected ones."""
        hashtag_clean = hashtag.lower().replace("#", "")

        for selected_tag in selected:
            selected_clean = selected_tag.lower().replace("#", "")

            # Check for exact match or substring
            if hashtag_clean == selected_clean:
                return True

            # Check for similar roots
            if len(hashtag_clean) > 4 and len(selected_clean) > 4:
                if hashtag_clean[:4] == selected_clean[:4]:
                    return True

        return False

    def _make_scannable(self, tweet: str) -> str:
        """Make tweet more scannable with formatting."""
        # Add bullet points for lists
        if "\n" in tweet and not tweet.startswith("•"):
            lines = tweet.split("\n")
            if len(lines) > 2:
                formatted_lines = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and not line.startswith(("•", "-", "*", "1.", "2.", "3.")):
                        if i > 0 and len(line) < 50:  # Short lines become bullet points
                            line = f"• {line}"
                    formatted_lines.append(line)
                tweet = "\n".join(formatted_lines)

        return tweet

    def _add_visual_separators(self, tweet: str) -> str:
        """Add visual separators for better structure."""
        # Add separators before important sections
        separators = ["---", "━━━", "▪▪▪"]

        # Only add if tweet is long enough and doesn't already have separators
        if len(tweet) > 200 and not any(sep in tweet for sep in separators):
            # Find natural break point
            sentences = tweet.split(". ")
            if len(sentences) > 2:
                mid_point = len(sentences) // 2
                separator = random.choice(separators)
                sentences.insert(mid_point, f"\n{separator}\n")
                tweet = ". ".join(sentences)

        return tweet

    def _optimize_lists(self, tweet: str) -> str:
        """Optimize bullet points and lists."""
        # Standardize bullet points
        tweet = re.sub(r'^[-*]\s+', '• ', tweet, flags=re.MULTILINE)

        # Add spacing around lists
        tweet = re.sub(r'([.!?])\n(• )', r'\1\n\n\2', tweet)

        return tweet

    def _apply_emphasis_formatting(self, tweet: str) -> str:
        """Apply emphasis formatting for key points."""
        # Emphasize numbers and percentages
        tweet = re.sub(r'\b(\d+%)\b', r'**\1**', tweet)

        # Emphasize key action words
        action_words = ["IMPORTANT", "KEY", "CRITICAL", "ESSENTIAL", "BREAKTHROUGH"]
        for word in action_words:
            if word in tweet:
                tweet = tweet.replace(word, f"**{word}**")

        return tweet

    def _has_emoji(self, text: str) -> bool:
        """Check if text already contains emojis."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return bool(emoji_pattern.search(text))

    def _has_psychological_trigger(self, text: str) -> bool:
        """Check if text already contains psychological triggers."""
        triggers = [
            "don't miss", "most people", "secret", "hidden", "surprising",
            "thousands", "experts", "proven", "industry", "top companies"
        ]
        return any(trigger in text.lower() for trigger in triggers)

    def _find_sentence_breaks(self, words: List[str]) -> List[int]:
        """Find natural break points in long sentences."""
        break_words = ["and", "but", "however", "therefore", "because", "since", "while", "when"]
        break_points = []

        for i, word in enumerate(words):
            if word.lower() in break_words and i > 5:  # Don't break too early
                break_points.append(i)

        return break_points

    def _convert_passive_to_active(self, text: str) -> str:
        """Convert basic passive voice patterns to active voice."""
        # Basic passive to active conversions
        conversions = [
            (r'is used by', 'uses'),
            (r'was created by', 'created'),
            (r'is implemented by', 'implements'),
            (r'is done by', 'does'),
            (r'is handled by', 'handles')
        ]

        for passive, active in conversions:
            text = re.sub(passive, active, text, flags=re.IGNORECASE)

        return text

    def _ensure_scannable_format(self, text: str) -> str:
        """Ensure text is in scannable format."""
        # Add line breaks before key phrases
        key_phrases = ["Here's how:", "The key is:", "Important:", "Remember:"]

        for phrase in key_phrases:
            if phrase in text and f"\n{phrase}" not in text:
                text = text.replace(phrase, f"\n\n{phrase}")

        return text

    def _add_personal_anecdote(self, tweet: str, content_type: str) -> str:
        """Add personal anecdotes to build credibility."""
        anecdote_templates = {
            "technical": [
                "After 5+ years in tech, I've learned that",
                "In my experience building production systems,",
                "Having debugged this issue countless times,",
                "From my time at [company], I discovered that",
                "After mentoring dozens of developers,"
            ],
            "tutorial": [
                "When I first started learning this,",
                "After teaching this to 100+ students,",
                "I wish someone had told me this when I started:",
                "The biggest mistake I made learning this was",
                "After years of trial and error,"
            ],
            "career": [
                "In my 10+ year career journey,",
                "After interviewing at 20+ companies,",
                "Having managed teams for 5+ years,",
                "From startup to Fortune 500,",
                "After climbing from junior to senior,"
            ],
            "business": [
                "After building 3 successful startups,",
                "Having raised $X in funding,",
                "From my experience scaling teams,",
                "After 100+ client projects,",
                "Having failed and succeeded multiple times,"
            ]
        }

        templates = anecdote_templates.get(content_type, anecdote_templates["technical"])

        # Only add if tweet doesn't already have personal elements
        if not self._has_personal_element(tweet):
            if random.random() < 0.4:  # 40% chance
                anecdote = random.choice(templates)
                # Insert naturally at the beginning
                tweet = f"{anecdote} {tweet.lower()}"

        return tweet

    def _add_case_study_reference(self, tweet: str, categories: List[str]) -> str:
        """Add case study references for credibility."""
        case_study_templates = {
            "programming": [
                "Netflix uses this pattern for their microservices",
                "Google's engineering team recommends this approach",
                "This is how Spotify handles their data pipeline",
                "Airbnb's architecture team implements this",
                "Facebook's React team suggests this pattern"
            ],
            "data-science": [
                "Uber's data science team uses this method",
                "Netflix's recommendation algorithm relies on this",
                "Google's ML engineers prefer this approach",
                "Tesla's autopilot team implements this",
                "Amazon's personalization engine uses this"
            ],
            "business": [
                "Apple used this strategy during their turnaround",
                "Amazon's growth was fueled by this principle",
                "Tesla's success comes from this approach",
                "Google's expansion followed this playbook",
                "Microsoft's transformation used this method"
            ],
            "career": [
                "Top tech companies look for this skill",
                "FAANG interviews focus on this concept",
                "Senior engineers at Google emphasize this",
                "Successful CTOs consistently do this",
                "High-performing teams always implement this"
            ]
        }

        # Find matching category
        for category in categories:
            if category in case_study_templates:
                if random.random() < 0.3:  # 30% chance
                    case_study = random.choice(case_study_templates[category])
                    # Add as supporting evidence
                    tweet = f"{tweet}\n\n💡 {case_study}."
                break

        return tweet

    def _add_authority_indicators(self, tweet: str, categories: List[str], position: int, total_tweets: int) -> str:
        """Add authority indicators and expertise signals."""
        authority_indicators = {
            "programming": [
                "industry best practice",
                "production-tested approach",
                "enterprise-grade solution",
                "battle-tested method",
                "scalable architecture pattern"
            ],
            "data-science": [
                "research-backed method",
                "peer-reviewed approach",
                "statistically significant results",
                "validated by experiments",
                "proven by A/B tests"
            ],
            "business": [
                "market-validated strategy",
                "investor-approved method",
                "revenue-generating approach",
                "growth-hacking technique",
                "ROI-positive strategy"
            ],
            "tutorial": [
                "beginner-friendly approach",
                "step-by-step methodology",
                "comprehensive framework",
                "structured learning path",
                "progressive skill building"
            ]
        }

        # Add authority indicators sparingly
        if random.random() < 0.2:  # 20% chance
            for category in categories:
                if category in authority_indicators:
                    indicator = random.choice(authority_indicators[category])
                    # Replace generic terms with authority terms
                    replacements = {
                        "method": indicator,
                        "approach": indicator,
                        "way": indicator,
                        "technique": indicator
                    }

                    for generic, authoritative in replacements.items():
                        if generic in tweet.lower():
                            tweet = re.sub(rf'\b{generic}\b', authoritative, tweet, count=1, flags=re.IGNORECASE)
                            break
                    break

        return tweet

    def _add_urgency_scarcity(self, tweet: str, position: int, total_tweets: int) -> str:
        """Add urgency and scarcity triggers."""
        urgency_phrases = [
            "Don't wait to implement this",
            "Start applying this today",
            "The sooner you start, the better",
            "Time is critical here",
            "Act on this immediately"
        ]

        scarcity_phrases = [
            "Only 10% of developers know this",
            "Most teams miss this opportunity",
            "Few people understand this concept",
            "This insight isn't widely known",
            "Rare to find this documented"
        ]

        # Add urgency to middle tweets
        if 0 < position < total_tweets - 1:
            if random.random() < 0.15:  # 15% chance
                if "important" in tweet.lower() or "critical" in tweet.lower():
                    urgency = random.choice(urgency_phrases)
                    tweet = f"{tweet}\n\n⚡ {urgency}."

        # Add scarcity to early tweets
        if position < total_tweets // 2:
            if random.random() < 0.1:  # 10% chance
                scarcity = random.choice(scarcity_phrases)
                tweet = f"{scarcity}:\n\n{tweet}"

        return tweet

    def _add_relatability_factors(self, tweet: str, content_type: str, categories: List[str]) -> str:
        """Add relatability factors based on content categories."""
        relatability_phrases = {
            "programming": [
                "We've all been there",
                "Every developer faces this",
                "Sound familiar?",
                "I bet you've experienced this",
                "This happens to the best of us"
            ],
            "career": [
                "We've all felt this way",
                "Every professional struggles with this",
                "You're not alone in this",
                "Most of us have been here",
                "This resonates with many"
            ],
            "tutorial": [
                "Learning this can be tricky",
                "This confuses many beginners",
                "Don't worry if this seems complex",
                "Everyone starts somewhere",
                "This takes practice to master"
            ],
            "business": [
                "Every entrepreneur faces this",
                "This challenge is universal",
                "We've all made this mistake",
                "This dilemma is common",
                "Most startups encounter this"
            ]
        }

        # Add relatability phrases
        if random.random() < 0.2:  # 20% chance
            for category in categories:
                if category in relatability_phrases:
                    phrase = random.choice(relatability_phrases[category])
                    # Add as empathetic opener or closer
                    if len(tweet) < 200:  # Short tweet - add at end
                        tweet = f"{tweet}\n\n{phrase} 🤝"
                    else:  # Long tweet - add at beginning
                        tweet = f"{phrase}:\n\n{tweet}"
                    break

        return tweet

    def _has_personal_element(self, text: str) -> bool:
        """Check if text already contains personal elements."""
        personal_indicators = [
            "i've", "my experience", "when i", "i learned", "i discovered",
            "after", "having", "from my", "in my", "i wish"
        ]
        return any(indicator in text.lower() for indicator in personal_indicators)

    def optimize_tweet_content(self, tweet_content: str, blog_post: 'BlogPost') -> str:
        """
        Optimize individual tweet content for maximum engagement.

        This is the main method called by the workflow to optimize tweet content.
        It combines multiple optimization techniques to enhance engagement.

        Args:
            tweet_content: The original tweet content to optimize
            blog_post: The blog post context for optimization

        Returns:
            Optimized tweet content
        """
        # Start with the original content
        optimized_content = tweet_content

        # Apply engagement elements (emojis, power words, psychological triggers)
        optimized_content = self.add_engagement_elements(
            optimized_content,
            position=0,  # Default position
            total_tweets=1,  # Single tweet optimization
            content_type=self._determine_content_type(blog_post.categories),
            categories=blog_post.categories
        )

        # Apply visual formatting for better readability
        optimized_content = self.apply_visual_formatting(optimized_content)

        # Add relatability factors
        optimized_content = self._add_relatability_factors(
            optimized_content,
            self._determine_content_type(blog_post.categories),
            blog_post.categories
        )

        # Ensure character count is within limits
        if len(optimized_content) > 280:
            # Truncate while preserving important elements
            optimized_content = self._truncate_preserving_elements(optimized_content)

        return optimized_content

    def _determine_content_type(self, categories: List[str]) -> str:
        """Determine content type from categories."""
        category_mapping = {
            "programming": "technical",
            "data-science": "technical",
            "machine-learning": "technical",
            "web-development": "technical",
            "tutorial": "educational",
            "career": "professional",
            "business": "business",
            "personal": "personal",
            "story": "personal"
        }

        for category in categories:
            if category in category_mapping:
                return category_mapping[category]

        return "general"

    def _truncate_preserving_elements(self, content: str) -> str:
        """Truncate content while preserving important engagement elements."""
        if len(content) <= 280:
            return content

        # Preserve emojis and hashtags at the end
        import re

        # Extract trailing emojis and hashtags
        trailing_pattern = r'(\s*[#@]\w+|\s*[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]+)*$'
        trailing_match = re.search(trailing_pattern, content)
        trailing_elements = trailing_match.group(0) if trailing_match else ""

        # Calculate available space
        available_space = 280 - len(trailing_elements)

        # Truncate main content
        main_content = content[:available_space - len(trailing_elements)].rstrip()

        # Find last complete sentence or phrase
        sentence_endings = ['. ', '! ', '? ', ': ', '\n']
        last_ending = -1

        for ending in sentence_endings:
            pos = main_content.rfind(ending)
            if pos > last_ending and pos > available_space * 0.7:  # At least 70% of content
                last_ending = pos + len(ending)

        if last_ending > 0:
            main_content = main_content[:last_ending].rstrip()
        else:
            # Fallback: truncate at word boundary
            words = main_content.split()
            while len(' '.join(words)) + len(trailing_elements) > 280 and words:
                words.pop()
            main_content = ' '.join(words)

        return main_content + trailing_elements