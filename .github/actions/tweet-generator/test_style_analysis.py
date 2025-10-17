"""
Comprehensive unit tests for style analysis functionality.

This module tests writing style analysis, vocabulary and tone extraction,
and profile persistence as specified in requirements 8.1, 8.2, and 8.3.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from style_analyzer import StyleAnalyzer
from models import (
    BlogPost, StyleProfile, VocabularyProfile, ToneProfile,
    StructureProfile, EmojiProfile
)
from exceptions import StyleAnalysisError


class TestStyleAnalyzer:
    """Test suite for StyleAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.posts_dir = self.temp_dir / "_posts"
        self.notebooks_dir = self.temp_dir / "_notebooks"
        self.generated_dir = self.temp_dir / ".generated"

        # Create directories
        self.posts_dir.mkdir(parents=True)
        self.notebooks_dir.mkdir(parents=True)
        self.generated_dir.mkdir(parents=True)

        # Initialize analyzer
        self.analyzer = StyleAnalyzer(min_posts=2)  # Lower threshold for testing

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_sample_blog_post(self, filename: str, frontmatter: dict, content: str) -> Path:
        """Create a sample blog post for testing."""
        file_path = self.posts_dir / filename

        # Build frontmatter
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}:")
                for item in value:
                    fm_lines.append(f"  - {item}")
            elif isinstance(value, bool):
                fm_lines.append(f"{key}: {str(value).lower()}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        fm_lines.append("")
        fm_lines.append(content)

        file_path.write_text("\n".join(fm_lines), encoding='utf-8')
        return file_path

    def create_technical_blog_post(self) -> BlogPost:
        """Create a technical blog post for testing."""
        content = """
        # Advanced Python Techniques

        In this tutorial, we'll explore advanced Python techniques that can significantly improve your code quality.

        ## Object-Oriented Programming

        First, let's discuss inheritance and polymorphism. These concepts are fundamental to understanding how Python handles class hierarchies.

        ```python
        class BaseClass:
            def __init__(self):
                self.value = 0

            def process_data(self):
                return self.value * 2
        ```

        The implementation above demonstrates a simple base class. However, we can extend this functionality using inheritance.

        ### Key Benefits

        - Improved code reusability
        - Better maintainability
        - Enhanced modularity
        - Cleaner architecture

        Furthermore, when working with APIs, you should always validate your input data. This ensures robust error handling.

        ## Conclusion

        These techniques will definitely help you write better Python code. What do you think about these approaches?
        """

        return BlogPost(
            file_path="2024-01-15-python-techniques.md",
            title="Advanced Python Techniques",
            content=content,
            frontmatter={
                "title": "Advanced Python Techniques",
                "categories": ["programming", "python", "tutorial"],
                "publish": True
            },
            canonical_url="https://example.com/python-techniques",
            categories=["programming", "python", "tutorial"],
            summary="Learn advanced Python techniques for better code quality"
        )

    def create_personal_blog_post(self) -> BlogPost:
        """Create a personal blog post for testing."""
        content = """
        # My Journey with Machine Learning

        Hey everyone! I wanted to share my personal experience learning machine learning over the past year.

        ## The Beginning

        When I first started, I was completely overwhelmed. There's so much information out there! I didn't know where to begin.

        I remember thinking, "How am I ever going to understand all of this?" But I decided to take it one step at a time.

        ## What I Learned

        Here's what really helped me:

        1. Start with the basics - don't jump into deep learning immediately
        2. Practice with real datasets - theory only goes so far
        3. Join communities - the support is amazing! 🚀

        I was surprised by how welcoming the ML community is. People are genuinely excited to help newcomers.

        ## My Advice

        If you're just starting out, don't worry! Everyone feels lost at first. The key is persistence and curiosity.

        What's your experience been like? I'd love to hear your stories! 😊

        P.S. - Feel free to reach out if you have questions. I'm always happy to chat about ML!
        """

        return BlogPost(
            file_path="2024-02-10-ml-journey.md",
            title="My Journey with Machine Learning",
            content=content,
            frontmatter={
                "title": "My Journey with Machine Learning",
                "categories": ["personal", "machine-learning", "career"],
                "publish": True
            },
            canonical_url="https://example.com/ml-journey",
            categories=["personal", "machine-learning", "career"],
            summary="Personal reflections on learning machine learning"
        )

    def create_formal_blog_post(self) -> BlogPost:
        """Create a formal academic-style blog post for testing."""
        content = """
        # An Analysis of Distributed Computing Paradigms

        ## Abstract

        This paper examines the fundamental principles underlying distributed computing architectures. We analyze various paradigms and their respective advantages and limitations.

        ## Introduction

        Distributed computing represents a significant advancement in computational methodology. Furthermore, it addresses scalability challenges inherent in traditional centralized systems.

        The primary objective of this analysis is to evaluate the effectiveness of different distributed computing approaches. Consequently, we examine several key metrics including performance, reliability, and maintainability.

        ## Methodology

        Our research methodology encompasses both theoretical analysis and empirical evaluation. Specifically, we conducted comprehensive benchmarking studies across multiple distributed systems.

        The evaluation criteria include:

        - Throughput performance metrics
        - Latency characteristics
        - Fault tolerance capabilities
        - Resource utilization efficiency

        ## Results and Discussion

        The results demonstrate that microservices architectures provide superior scalability compared to monolithic designs. However, they introduce additional complexity in terms of service orchestration and monitoring.

        Moreover, the implementation of distributed consensus algorithms significantly impacts system performance. Therefore, careful consideration must be given to algorithm selection based on specific use case requirements.

        ## Conclusion

        In conclusion, distributed computing paradigms offer substantial benefits for large-scale applications. Nevertheless, the increased architectural complexity requires careful design and implementation strategies.

        Future research should focus on automated optimization techniques for distributed system configuration and management.
        """

        return BlogPost(
            file_path="2024-03-05-distributed-computing.md",
            title="An Analysis of Distributed Computing Paradigms",
            content=content,
            frontmatter={
                "title": "An Analysis of Distributed Computing Paradigms",
                "categories": ["research", "distributed-systems", "computer-science"],
                "publish": True
            },
            canonical_url="https://example.com/distributed-computing",
            categories=["research", "distributed-systems", "computer-science"],
            summary="Academic analysis of distributed computing approaches"
        )

    def create_sample_posts_for_analysis(self) -> list:
        """Create a diverse set of blog posts for comprehensive testing."""
        posts = []

        # Technical post
        tech_post = self.create_technical_blog_post()
        self.create_sample_blog_post("tech-post.md", tech_post.frontmatter, tech_post.content)
        posts.append(tech_post)

        # Personal post
        personal_post = self.create_personal_blog_post()
        self.create_sample_blog_post("personal-post.md", personal_post.frontmatter, personal_post.content)
        posts.append(personal_post)

        # Formal post
        formal_post = self.create_formal_blog_post()
        self.create_sample_blog_post("formal-post.md", formal_post.frontmatter, formal_post.content)
        posts.append(formal_post)

        return posts

    # Test vocabulary analysis functionality

    def test_vocabulary_analysis_with_technical_content(self):
        """Test vocabulary analysis with technical blog posts."""
        # Create technical content with repeated technical terms (needed for detection)
        content = [
            "We'll implement a REST API using Python and Flask. The API authentication system uses JWT tokens.",
            "The database schema includes user tables with foreign key relationships. We use database connections for ORM.",
            "Error handling is crucial for robust applications. Always validate input data and handle errors properly.",
            "Python development requires good error handling practices. Use Python best practices for API development."
        ]

        vocab_profile = self.analyzer.analyze_vocabulary_patterns(content)

        # Verify vocabulary profile structure
        assert isinstance(vocab_profile, VocabularyProfile)
        assert isinstance(vocab_profile.common_words, list)
        assert isinstance(vocab_profile.technical_terms, list)
        assert isinstance(vocab_profile.word_frequency, dict)
        assert isinstance(vocab_profile.average_word_length, float)
        assert isinstance(vocab_profile.vocabulary_diversity, float)

        # Check for technical terms detection (terms need to appear at least twice)
        expected_technical_terms = ['api', 'python', 'error', 'database']
        found_technical_terms = [term.lower() for term in vocab_profile.technical_terms]

        # At least some technical terms should be detected
        technical_terms_found = sum(1 for term in expected_technical_terms
                                  if any(term in found_term for found_term in found_technical_terms))
        assert technical_terms_found > 0, f"No technical terms detected. Found: {found_technical_terms}"

        # Verify metrics are reasonable
        assert 0 < vocab_profile.average_word_length < 20
        assert 0 < vocab_profile.vocabulary_diversity <= 1.0

    def test_vocabulary_analysis_with_personal_content(self):
        """Test vocabulary analysis with personal blog posts."""
        content = [
            "I'm really excited to share my journey with you! It's been amazing so far.",
            "When I started, I was nervous but the community was super welcoming and helpful.",
            "I'd love to hear about your experiences too. Feel free to reach out anytime!"
        ]

        vocab_profile = self.analyzer.analyze_vocabulary_patterns(content)

        # Check for personal language patterns
        common_words_lower = [word.lower() for word in vocab_profile.common_words]
        personal_indicators = ['excited', 'amazing', 'love', 'feel', 'share']

        found_personal_words = sum(1 for word in personal_indicators if word in common_words_lower)
        assert found_personal_words > 0, "Personal vocabulary indicators not detected"

        # Verify informal language patterns (contractions are processed differently)
        # Check for personal pronouns and informal words instead
        informal_indicators = ['really', 'super', 'amazing', 'love']
        found_informal = sum(1 for word in informal_indicators if word in common_words_lower)
        assert found_informal > 0, "Informal language indicators not detected"

    def test_vocabulary_analysis_empty_content(self):
        """Test vocabulary analysis with empty content."""
        vocab_profile = self.analyzer.analyze_vocabulary_patterns([])

        assert vocab_profile.common_words == []
        assert vocab_profile.technical_terms == []
        assert vocab_profile.word_frequency == {}
        assert vocab_profile.average_word_length == 0.0
        assert vocab_profile.vocabulary_diversity == 0.0

    # Test tone analysis functionality

    def test_tone_analysis_enthusiastic_content(self):
        """Test tone analysis with enthusiastic content."""
        content = [
            "This is absolutely amazing! I'm so excited to share this incredible discovery with you!",
            "The results are fantastic and I definitely recommend trying this approach!",
            "You'll love how simple and effective this solution is!"
        ]

        tone_profile = self.analyzer.extract_tone_indicators(content)

        # Verify tone profile structure
        assert isinstance(tone_profile, ToneProfile)
        assert 0.0 <= tone_profile.formality_level <= 1.0
        assert 0.0 <= tone_profile.enthusiasm_level <= 1.0
        assert 0.0 <= tone_profile.confidence_level <= 1.0
        assert 0.0 <= tone_profile.humor_usage <= 1.0

        # Check enthusiasm detection
        assert tone_profile.enthusiasm_level > 0.5, f"Expected high enthusiasm, got {tone_profile.enthusiasm_level}"

        # Check exclamation frequency
        assert tone_profile.exclamation_frequency > 0, "Exclamation marks not detected"

    def test_tone_analysis_formal_content(self):
        """Test tone analysis with formal academic content."""
        content = [
            "This research demonstrates the effectiveness of the proposed methodology.",
            "Furthermore, the results indicate significant improvements in performance metrics.",
            "Consequently, we recommend implementing these techniques in production environments."
        ]

        tone_profile = self.analyzer.extract_tone_indicators(content)

        # Check formality detection
        assert tone_profile.formality_level > 0.6, f"Expected high formality, got {tone_profile.formality_level}"

        # Check confidence level (formal language tends to be confident)
        assert tone_profile.confidence_level > 0.4, f"Expected moderate confidence, got {tone_profile.confidence_level}"

    def test_tone_analysis_personal_anecdotes(self):
        """Test detection of personal anecdotes."""
        content = [
            "When I first started learning programming, I was completely lost.",
            "I remember thinking that I would never understand pointers in C.",
            "My experience with debugging taught me patience and persistence."
        ]

        tone_profile = self.analyzer.extract_tone_indicators(content)

        # Check personal anecdote detection
        assert tone_profile.personal_anecdotes == True, "Personal anecdotes not detected"

    def test_tone_analysis_question_frequency(self):
        """Test question frequency detection."""
        content = [
            "What do you think about this approach? Have you tried something similar?",
            "How would you solve this problem? What are your thoughts?",
            "This is a statement without questions."
        ]

        tone_profile = self.analyzer.extract_tone_indicators(content)

        # Check question frequency
        assert tone_profile.question_frequency > 0, "Questions not detected"
        assert tone_profile.question_frequency < 1.0, "Question frequency should be less than 1.0"

    # Test structure analysis functionality

    def test_structure_analysis_with_lists(self):
        """Test structure analysis with list-heavy content."""
        posts = [
            BlogPost(
                file_path="list-post.md",
                title="List Post",
                content="""
                # Main Topic

                Here are the key points:

                - First important point
                - Second crucial detail
                - Third essential item

                Additionally, consider these steps:

                1. Initialize the system
                2. Configure the parameters
                3. Execute the process
                4. Validate the results
                """,
                frontmatter={},
                canonical_url="https://example.com/list-post",
                categories=["tutorial"]
            )
        ]

        structure_profile = self.analyzer.identify_content_structures(posts)

        # Verify structure profile
        assert isinstance(structure_profile, StructureProfile)
        assert structure_profile.list_usage_frequency > 0, "List usage not detected"
        assert isinstance(structure_profile.header_usage_patterns, list)

    def test_structure_analysis_with_code_blocks(self):
        """Test structure analysis with code blocks."""
        posts = [
            BlogPost(
                file_path="code-post.md",
                title="Code Post",
                content="""
                # Programming Tutorial

                Here's a simple function:

                ```python
                def hello_world():
                    print("Hello, World!")
                    return True
                ```

                You can also use inline code like `print()` or `len()` functions.

                Another example:

                ```javascript
                function greet(name) {
                    console.log(`Hello, ${name}!`);
                }
                ```
                """,
                frontmatter={},
                canonical_url="https://example.com/code-post",
                categories=["programming"]
            )
        ]

        structure_profile = self.analyzer.identify_content_structures(posts)

        # Check code block detection
        assert structure_profile.code_block_frequency > 0, "Code blocks not detected"

    def test_structure_analysis_sentence_length(self):
        """Test average sentence length calculation."""
        posts = [
            BlogPost(
                file_path="sentence-test.md",
                title="Sentence Test",
                content="""
                Short sentence. This is a medium-length sentence with some details.
                This is a much longer sentence that contains multiple clauses and provides extensive information about the topic being discussed.
                """,
                frontmatter={},
                canonical_url="https://example.com/sentence-test",
                categories=["test"]
            )
        ]

        structure_profile = self.analyzer.identify_content_structures(posts)

        # Verify sentence length calculation
        assert structure_profile.average_sentence_length > 0, "Average sentence length not calculated"
        assert structure_profile.average_sentence_length < 50, "Average sentence length seems too high"

    # Test emoji analysis functionality

    def test_emoji_analysis_with_emojis(self):
        """Test emoji analysis with emoji-rich content."""
        content = [
            "I'm so excited about this project! 🚀 It's going to be amazing! ✨",
            "Check out this cool feature 😎 You'll love it! ❤️",
            "Happy coding everyone! 💻 Let's build something awesome! 🎉"
        ]

        emoji_profile = self.analyzer.analyze_emoji_usage(content)

        # Verify emoji profile structure
        assert isinstance(emoji_profile, EmojiProfile)
        assert emoji_profile.emoji_frequency > 0, "Emoji frequency not calculated"
        assert len(emoji_profile.common_emojis) > 0, "Common emojis not detected"
        assert emoji_profile.emoji_placement in ["start", "middle", "end"], "Invalid emoji placement"

    def test_emoji_analysis_technical_emojis(self):
        """Test detection of technical emojis."""
        content = [
            "Working on the new API 💻 The database optimization is complete 📊",
            "Debugging the authentication system 🔧 Fixed the memory leak! ⚡",
            "Code review time 📝 Everything looks good 💾"
        ]

        emoji_profile = self.analyzer.analyze_emoji_usage(content)

        # Check technical emoji detection
        assert emoji_profile.technical_emoji_usage == True, "Technical emoji usage not detected"

    def test_emoji_analysis_no_emojis(self):
        """Test emoji analysis with content containing no emojis."""
        content = [
            "This is a regular blog post without any emojis.",
            "It contains technical information and explanations.",
            "The content is purely text-based."
        ]

        emoji_profile = self.analyzer.analyze_emoji_usage(content)

        # Verify empty emoji profile
        assert emoji_profile.emoji_frequency == 0.0, "Emoji frequency should be 0"
        assert emoji_profile.common_emojis == [], "Common emojis should be empty"
        assert emoji_profile.technical_emoji_usage == False, "Technical emoji usage should be False"

    # Test complete style profile building

    @patch('style_analyzer.ContentDetector')
    def test_build_style_profile_success(self, mock_detector_class):
        """Test successful style profile building."""
        # Mock ContentDetector
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector

        # Create sample posts
        sample_posts = self.create_sample_posts_for_analysis()
        mock_detector.get_all_posts.return_value = sample_posts

        # Build style profile
        style_profile = self.analyzer.build_style_profile(
            str(self.posts_dir),
            str(self.notebooks_dir)
        )

        # Verify style profile structure
        assert isinstance(style_profile, StyleProfile)
        assert isinstance(style_profile.vocabulary_patterns, VocabularyProfile)
        assert isinstance(style_profile.tone_indicators, ToneProfile)
        assert isinstance(style_profile.content_structures, StructureProfile)
        assert isinstance(style_profile.emoji_usage, EmojiProfile)
        assert style_profile.posts_analyzed == len(sample_posts)
        assert style_profile.version == "1.0.0"

        # Verify that analysis was performed
        assert len(style_profile.vocabulary_patterns.common_words) > 0
        assert style_profile.tone_indicators.formality_level >= 0.0

    @patch('style_analyzer.ContentDetector')
    def test_build_style_profile_insufficient_posts(self, mock_detector_class):
        """Test style profile building with insufficient posts."""
        # Mock ContentDetector with insufficient posts
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detector.get_all_posts.return_value = [self.create_technical_blog_post()]  # Only 1 post

        # Should raise StyleAnalysisError
        with pytest.raises(StyleAnalysisError) as exc_info:
            self.analyzer.build_style_profile(str(self.posts_dir), str(self.notebooks_dir))

        assert "Insufficient content for analysis" in str(exc_info.value)

    @patch('style_analyzer.ContentDetector')
    def test_build_style_profile_no_content(self, mock_detector_class):
        """Test style profile building with posts containing no content."""
        # Mock ContentDetector with empty content posts
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector

        empty_posts = [
            BlogPost(
                file_path="empty1.md",
                title="Empty Post 1",
                content="",
                frontmatter={},
                canonical_url="https://example.com/empty1",
                categories=[]
            ),
            BlogPost(
                file_path="empty2.md",
                title="Empty Post 2",
                content="   ",  # Only whitespace
                frontmatter={},
                canonical_url="https://example.com/empty2",
                categories=[]
            )
        ]
        mock_detector.get_all_posts.return_value = empty_posts

        # Should raise StyleAnalysisError
        with pytest.raises(StyleAnalysisError) as exc_info:
            self.analyzer.build_style_profile(str(self.posts_dir), str(self.notebooks_dir))

        assert "No valid content found" in str(exc_info.value)

    # Test profile persistence functionality

    def test_save_style_profile_success(self):
        """Test successful style profile saving."""
        # Create a sample style profile
        style_profile = StyleProfile(
            vocabulary_patterns=VocabularyProfile(
                common_words=["test", "example", "sample"],
                technical_terms=["api", "database"],
                word_frequency={"test": 5, "example": 3},
                average_word_length=5.2,
                vocabulary_diversity=0.75
            ),
            tone_indicators=ToneProfile(
                formality_level=0.6,
                enthusiasm_level=0.4,
                confidence_level=0.7,
                personal_anecdotes=True
            ),
            posts_analyzed=3,
            version="1.0.0"
        )

        # Save profile
        output_path = str(self.generated_dir / "test-style-profile.json")
        self.analyzer.save_style_profile(style_profile, output_path)

        # Verify file was created
        assert Path(output_path).exists(), "Style profile file was not created"

        # Verify file content
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert "vocabulary_patterns" in saved_data
        assert "tone_indicators" in saved_data
        assert "content_structures" in saved_data
        assert "emoji_usage" in saved_data
        assert "metadata" in saved_data
        assert saved_data["posts_analyzed"] == 3
        assert saved_data["version"] == "1.0.0"

    def test_load_style_profile_success(self):
        """Test successful style profile loading."""
        # Create and save a style profile first
        original_profile = StyleProfile(
            vocabulary_patterns=VocabularyProfile(
                common_words=["load", "test", "profile"],
                technical_terms=["json", "data"],
                average_word_length=4.8
            ),
            tone_indicators=ToneProfile(
                formality_level=0.5,
                enthusiasm_level=0.3
            ),
            posts_analyzed=2,
            version="1.0.0"
        )

        profile_path = str(self.generated_dir / "load-test-profile.json")
        self.analyzer.save_style_profile(original_profile, profile_path)

        # Load the profile
        loaded_profile = self.analyzer.load_style_profile(profile_path)

        # Verify loaded profile matches original
        assert isinstance(loaded_profile, StyleProfile)
        assert loaded_profile.posts_analyzed == original_profile.posts_analyzed
        assert loaded_profile.version == original_profile.version
        assert loaded_profile.vocabulary_patterns.common_words == original_profile.vocabulary_patterns.common_words
        assert loaded_profile.tone_indicators.formality_level == original_profile.tone_indicators.formality_level

    def test_load_style_profile_file_not_found(self):
        """Test loading style profile from non-existent file."""
        non_existent_path = str(self.generated_dir / "non-existent-profile.json")

        with pytest.raises(StyleAnalysisError) as exc_info:
            self.analyzer.load_style_profile(non_existent_path)

        assert "Style profile file not found" in str(exc_info.value)

    def test_load_style_profile_invalid_format(self):
        """Test loading style profile with invalid format version."""
        # Create a profile with unsupported format version
        invalid_profile_data = {
            "vocabulary_patterns": {},
            "tone_indicators": {},
            "content_structures": {},
            "emoji_usage": {},
            "posts_analyzed": 1,
            "version": "1.0.0",
            "metadata": {
                "format_version": "2.0.0"  # Unsupported version
            }
        }

        profile_path = str(self.generated_dir / "invalid-format-profile.json")
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_profile_data, f)

        with pytest.raises(StyleAnalysisError) as exc_info:
            self.analyzer.load_style_profile(profile_path)

        assert "Unsupported profile format version" in str(exc_info.value)

    # Test integration scenarios

    def test_style_analysis_with_mixed_content_types(self):
        """Test style analysis with mixed content types (technical, personal, formal)."""
        # Create mixed content
        mixed_posts = self.create_sample_posts_for_analysis()

        # Mock ContentDetector for integration test
        with patch('style_analyzer.ContentDetector') as mock_detector_class:
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector
            mock_detector.get_all_posts.return_value = mixed_posts

            # Build comprehensive style profile
            style_profile = self.analyzer.build_style_profile(
                str(self.posts_dir),
                str(self.notebooks_dir)
            )

            # Verify comprehensive analysis
            assert style_profile.posts_analyzed == len(mixed_posts)

            # Should detect both technical and personal elements
            vocab = style_profile.vocabulary_patterns
            assert len(vocab.common_words) > 10, "Should have substantial vocabulary"
            assert len(vocab.technical_terms) > 0, "Should detect technical terms"

            # Should have balanced tone indicators
            tone = style_profile.tone_indicators
            assert 0.0 <= tone.formality_level <= 1.0
            assert 0.0 <= tone.enthusiasm_level <= 1.0
            assert 0.0 <= tone.confidence_level <= 1.0

    def test_style_profile_persistence_roundtrip(self):
        """Test complete save and load cycle for style profile."""
        # Create comprehensive style profile
        original_profile = StyleProfile(
            vocabulary_patterns=VocabularyProfile(
                common_words=["comprehensive", "test", "analysis", "profile"],
                technical_terms=["api", "database", "json", "http"],
                word_frequency={"test": 10, "analysis": 8, "profile": 6},
                average_word_length=6.2,
                vocabulary_diversity=0.82,
                preferred_synonyms={"use": "utilize", "help": "assist"}
            ),
            tone_indicators=ToneProfile(
                formality_level=0.65,
                enthusiasm_level=0.45,
                confidence_level=0.78,
                humor_usage=0.12,
                personal_anecdotes=True,
                question_frequency=0.15,
                exclamation_frequency=0.08
            ),
            content_structures=StructureProfile(
                average_sentence_length=18.5,
                paragraph_length_preference="medium",
                list_usage_frequency=2.3,
                code_block_frequency=1.8,
                header_usage_patterns=["H1", "H2", "H3"],
                preferred_transitions=["however", "furthermore", "additionally"]
            ),
            emoji_usage=EmojiProfile(
                emoji_frequency=1.2,
                common_emojis=["🚀", "💻", "✨"],
                emoji_placement="end",
                technical_emoji_usage=True
            ),
            posts_analyzed=5,
            version="1.0.0"
        )

        # Save and load profile
        profile_path = str(self.generated_dir / "roundtrip-test-profile.json")
        self.analyzer.save_style_profile(original_profile, profile_path)
        loaded_profile = self.analyzer.load_style_profile(profile_path)

        # Verify all components match
        assert loaded_profile.posts_analyzed == original_profile.posts_analyzed
        assert loaded_profile.version == original_profile.version

        # Vocabulary patterns
        assert loaded_profile.vocabulary_patterns.common_words == original_profile.vocabulary_patterns.common_words
        assert loaded_profile.vocabulary_patterns.technical_terms == original_profile.vocabulary_patterns.technical_terms
        assert loaded_profile.vocabulary_patterns.average_word_length == original_profile.vocabulary_patterns.average_word_length

        # Tone indicators
        assert loaded_profile.tone_indicators.formality_level == original_profile.tone_indicators.formality_level
        assert loaded_profile.tone_indicators.personal_anecdotes == original_profile.tone_indicators.personal_anecdotes

        # Content structures
        assert loaded_profile.content_structures.paragraph_length_preference == original_profile.content_structures.paragraph_length_preference
        assert loaded_profile.content_structures.header_usage_patterns == original_profile.content_structures.header_usage_patterns

        # Emoji usage
        assert loaded_profile.emoji_usage.common_emojis == original_profile.emoji_usage.common_emojis
        assert loaded_profile.emoji_usage.technical_emoji_usage == original_profile.emoji_usage.technical_emoji_usage

    def test_error_handling_in_analysis_methods(self):
        """Test error handling in individual analysis methods."""
        # Test with malformed content that might cause errors
        problematic_content = [
            "",  # Empty string
            "   ",  # Only whitespace
            "🚀" * 1000,  # Only emojis
            "a" * 10000,  # Very long single word
        ]

        # Should not raise exceptions, but handle gracefully
        vocab_profile = self.analyzer.analyze_vocabulary_patterns(problematic_content)
        assert isinstance(vocab_profile, VocabularyProfile)

        tone_profile = self.analyzer.extract_tone_indicators(problematic_content)
        assert isinstance(tone_profile, ToneProfile)

        emoji_profile = self.analyzer.analyze_emoji_usage(problematic_content)
        assert isinstance(emoji_profile, EmojiProfile)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])