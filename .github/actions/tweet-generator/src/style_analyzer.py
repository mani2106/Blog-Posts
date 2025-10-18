"""
Writing style analysis for the Tweet Thread Generator.

This module analyzes existing blog content to build comprehensive writing style profiles
that capture the author's voice, tone, vocabulary patterns, and content preferences.
"""

import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime

from models import (
    BlogPost, StyleProfile, VocabularyProfile, ToneProfile,
    StructureProfile, EmojiProfile
)
from exceptions import StyleAnalysisError
from utils import save_json_file, load_json_file, count_words, count_sentences
from content_detector import ContentDetector


class StyleAnalyzer:
    """Analyzes writing style from existing blog content."""

    def __init__(self, min_posts: int = 3):
        """
        Initialize style analyzer.

        Args:
            min_posts: Minimum number of posts required for analysis
        """
        self.min_posts = min_posts

    def build_style_profile(self, posts_dir: str, notebooks_dir: str) -> StyleProfile:
        """
        Build comprehensive writing style profile from existing content.

        Args:
            posts_dir: Directory containing markdown blog posts
            notebooks_dir: Directory containing Jupyter notebook posts

        Returns:
            StyleProfile object with analysis results

        Raises:
            StyleAnalysisError: If analysis fails or insufficient content
        """
        try:
            # Initialize content detector to get all posts
            detector = ContentDetector(posts_dir, notebooks_dir)
            all_posts = detector.get_all_posts()

            if len(all_posts) < self.min_posts:
                raise StyleAnalysisError(
                    f"Insufficient content for analysis. Found {len(all_posts)} posts, minimum {self.min_posts} required.",
                    {"posts_found": len(all_posts), "min_required": self.min_posts}
                )

            # Extract content for analysis
            content_texts = [post.content for post in all_posts if post.content.strip()]

            if not content_texts:
                raise StyleAnalysisError("No valid content found in posts")

            # Perform analysis
            vocabulary_profile = self.analyze_vocabulary_patterns(content_texts)
            tone_profile = self.extract_tone_indicators(content_texts)
            structure_profile = self.identify_content_structures(all_posts)
            emoji_profile = self.analyze_emoji_usage(content_texts)

            # Create comprehensive style profile
            style_profile = StyleProfile(
                vocabulary_patterns=vocabulary_profile,
                tone_indicators=tone_profile,
                content_structures=structure_profile,
                emoji_usage=emoji_profile,
                created_at=datetime.now(),
                version="1.0.0",
                posts_analyzed=len(all_posts)
            )

            return style_profile

        except Exception as e:
            if isinstance(e, StyleAnalysisError):
                raise
            raise StyleAnalysisError(f"Failed to build style profile: {e}")

    def analyze_vocabulary_patterns(self, content: List[str]) -> VocabularyProfile:
        """
        Analyze vocabulary patterns and word usage.

        Args:
            content: List of text content to analyze

        Returns:
            VocabularyProfile with vocabulary analysis
        """
        try:
            # Combine all content for analysis
            combined_text = ' '.join(content)

            # Clean and tokenize text
            words = self._extract_words(combined_text)

            if not words:
                return VocabularyProfile()

            # Calculate word frequency
            word_freq = Counter(words)
            total_words = len(words)

            # Get most common words (excluding stop words)
            stop_words = self._get_stop_words()
            content_words = [word for word in words if word.lower() not in stop_words]
            content_word_freq = Counter(content_words)

            # Extract common words (top 50 content words)
            common_words = [word for word, _ in content_word_freq.most_common(50)]

            # Identify technical terms (words with specific patterns)
            technical_terms = self._identify_technical_terms(words)

            # Calculate average word length
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0.0

            # Calculate vocabulary diversity (unique words / total words)
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / total_words if total_words > 0 else 0.0

            # Identify preferred synonyms (words that appear together frequently)
            preferred_synonyms = self._find_preferred_synonyms(words)

            return VocabularyProfile(
                common_words=common_words,
                technical_terms=technical_terms,
                word_frequency=dict(word_freq.most_common(100)),  # Top 100 words
                average_word_length=avg_word_length,
                vocabulary_diversity=vocabulary_diversity,
                preferred_synonyms=preferred_synonyms
            )

        except Exception as e:
            raise StyleAnalysisError(f"Failed to analyze vocabulary patterns: {e}")

    def extract_tone_indicators(self, content: List[str]) -> ToneProfile:
        """
        Extract tone and sentiment indicators from content.

        Args:
            content: List of text content to analyze

        Returns:
            ToneProfile with tone analysis
        """
        try:
            combined_text = ' '.join(content)

            # Count total sentences for frequency calculations
            total_sentences = sum(count_sentences(text) for text in content)
            total_words = sum(count_words(text) for text in content)

            if total_sentences == 0 or total_words == 0:
                return ToneProfile()

            # Analyze formality level
            formality_level = self._analyze_formality(combined_text, total_words)

            # Analyze enthusiasm level
            enthusiasm_level = self._analyze_enthusiasm(combined_text, total_words)

            # Analyze confidence level
            confidence_level = self._analyze_confidence(combined_text, total_words)

            # Analyze humor usage
            humor_usage = self._analyze_humor(combined_text, total_words)

            # Check for personal anecdotes
            personal_anecdotes = self._detect_personal_anecdotes(combined_text)

            # Calculate question frequency
            question_count = combined_text.count('?')
            question_frequency = question_count / total_sentences

            # Calculate exclamation frequency
            exclamation_count = combined_text.count('!')
            exclamation_frequency = exclamation_count / total_sentences

            return ToneProfile(
                formality_level=formality_level,
                enthusiasm_level=enthusiasm_level,
                confidence_level=confidence_level,
                humor_usage=humor_usage,
                personal_anecdotes=personal_anecdotes,
                question_frequency=question_frequency,
                exclamation_frequency=exclamation_frequency
            )

        except Exception as e:
            raise StyleAnalysisError(f"Failed to extract tone indicators: {e}")

    def identify_content_structures(self, posts: List[BlogPost]) -> StructureProfile:
        """
        Identify content structure and formatting preferences.

        Args:
            posts: List of BlogPost objects to analyze

        Returns:
            StructureProfile with structure analysis
        """
        try:
            if not posts:
                return StructureProfile()

            # Analyze sentence length patterns
            all_sentences = []
            for post in posts:
                sentences = self._extract_sentences(post.content)
                all_sentences.extend(sentences)

            if not all_sentences:
                return StructureProfile()

            # Calculate average sentence length
            sentence_lengths = [len(sentence.split()) for sentence in all_sentences]
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

            # Analyze paragraph preferences
            paragraph_preference = self._analyze_paragraph_preference(posts)

            # Analyze list usage frequency
            list_usage_freq = self._analyze_list_usage(posts)

            # Analyze code block frequency
            code_block_freq = self._analyze_code_block_usage(posts)

            # Extract header usage patterns
            header_patterns = self._analyze_header_patterns(posts)

            # Identify preferred transitions
            preferred_transitions = self._identify_transitions(posts)

            return StructureProfile(
                average_sentence_length=avg_sentence_length,
                paragraph_length_preference=paragraph_preference,
                list_usage_frequency=list_usage_freq,
                code_block_frequency=code_block_freq,
                header_usage_patterns=header_patterns,
                preferred_transitions=preferred_transitions
            )

        except Exception as e:
            raise StyleAnalysisError(f"Failed to identify content structures: {e}")

    def analyze_emoji_usage(self, content: List[str]) -> EmojiProfile:
        """
        Analyze emoji usage patterns.

        Args:
            content: List of text content to analyze

        Returns:
            EmojiProfile with emoji usage analysis
        """
        try:
            combined_text = ' '.join(content)

            # Extract emojis using Unicode ranges
            emojis = self._extract_emojis(combined_text)

            if not emojis:
                return EmojiProfile(
                    emoji_frequency=0.0,
                    common_emojis=[],
                    emoji_placement="end",
                    technical_emoji_usage=False
                )

            # Calculate emoji frequency (emojis per 1000 characters)
            total_chars = len(combined_text)
            emoji_frequency = (len(emojis) / total_chars * 1000) if total_chars > 0 else 0.0

            # Find most common emojis
            emoji_counter = Counter(emojis)
            common_emojis = [emoji for emoji, _ in emoji_counter.most_common(10)]

            # Analyze emoji placement patterns
            emoji_placement = self._analyze_emoji_placement(content)

            # Check for technical emoji usage (code-related emojis)
            technical_emoji_usage = self._detect_technical_emoji_usage(emojis)

            return EmojiProfile(
                emoji_frequency=emoji_frequency,
                common_emojis=common_emojis,
                emoji_placement=emoji_placement,
                technical_emoji_usage=technical_emoji_usage
            )

        except Exception as e:
            raise StyleAnalysisError(f"Failed to analyze emoji usage: {e}")

    def save_style_profile(self, profile: StyleProfile, output_path: str) -> None:
        """
        Save style profile to JSON file.

        Args:
            profile: StyleProfile to save
            output_path: Path to save the profile

        Raises:
            StyleAnalysisError: If saving fails
        """
        try:
            # Convert profile to dictionary for JSON serialization
            profile_data = profile.to_dict()

            # Add metadata for version control
            profile_data["metadata"] = {
                "generator_version": "1.0.0",
                "saved_at": datetime.now().isoformat(),
                "format_version": "1.0.0"
            }

            # Save to JSON file
            success = save_json_file(profile_data, output_path, indent=2)

            if not success:
                raise StyleAnalysisError(f"Failed to save style profile to {output_path}")

        except Exception as e:
            if isinstance(e, StyleAnalysisError):
                raise
            raise StyleAnalysisError(f"Failed to save style profile: {e}")

    def load_style_profile(self, profile_path: str) -> StyleProfile:
        """
        Load existing style profile from JSON file.

        Args:
            profile_path: Path to the style profile file

        Returns:
            StyleProfile object

        Raises:
            StyleAnalysisError: If loading fails
        """
        try:
            # Load JSON data
            profile_data = load_json_file(profile_path)

            if profile_data is None:
                raise StyleAnalysisError(f"Style profile file not found: {profile_path}")

            # Validate format version if present
            metadata = profile_data.get("metadata", {})
            format_version = metadata.get("format_version", "1.0.0")

            if format_version != "1.0.0":
                raise StyleAnalysisError(
                    f"Unsupported profile format version: {format_version}",
                    {"supported_version": "1.0.0", "found_version": format_version}
                )

            # Create StyleProfile from dictionary
            style_profile = StyleProfile.from_dict(profile_data)

            return style_profile

        except Exception as e:
            if isinstance(e, StyleAnalysisError):
                raise
            raise StyleAnalysisError(f"Failed to load style profile: {e}")

    # Helper methods for vocabulary analysis

    def _extract_words(self, text: str) -> List[str]:
        """Extract and clean words from text."""
        # Remove markdown formatting and code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`[^`]+`', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'[#*_~]', '', text)  # Markdown formatting

        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        # Filter out very short words and common noise
        words = [word for word in words if len(word) >= 2]

        return words

    def _get_stop_words(self) -> Set[str]:
        """Get common English stop words."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'now'
        }

    def _identify_technical_terms(self, words: List[str]) -> List[str]:
        """Identify technical terms based on patterns."""
        technical_patterns = [
            r'^[a-z]+[A-Z]',  # camelCase
            r'^[A-Z][a-z]*[A-Z]',  # PascalCase
            r'.*[0-9].*',  # Contains numbers
            r'.*(api|http|url|json|xml|css|html|js|py|sql|db).*',  # Tech keywords
            r'.*(config|setup|init|auth|token|key|secret).*',  # Config terms
            r'.*(test|debug|log|error|exception|bug).*',  # Development terms
        ]

        technical_terms = set()
        for word in words:
            for pattern in technical_patterns:
                if re.match(pattern, word, re.IGNORECASE):
                    technical_terms.add(word.lower())
                    break

        # Filter by frequency - only include terms that appear multiple times
        word_freq = Counter(words)
        frequent_technical = [term for term in technical_terms
                            if word_freq.get(term, 0) >= 2]

        return sorted(frequent_technical)[:20]  # Top 20 technical terms

    def _find_preferred_synonyms(self, words: List[str]) -> Dict[str, str]:
        """Find preferred word choices by analyzing context."""
        # Simple implementation - look for common synonym pairs
        synonym_pairs = {
            ('use', 'utilize'): 'use',
            ('help', 'assist'): 'help',
            ('show', 'demonstrate'): 'show',
            ('make', 'create'): 'create',
            ('get', 'obtain'): 'get',
            ('start', 'begin'): 'start',
            ('end', 'finish'): 'end',
            ('big', 'large'): 'big',
            ('small', 'little'): 'small'
        }

        word_freq = Counter(words)
        preferred = {}

        for (word1, word2), default in synonym_pairs.items():
            freq1 = word_freq.get(word1, 0)
            freq2 = word_freq.get(word2, 0)

            if freq1 > 0 or freq2 > 0:
                if freq1 >= freq2:
                    preferred[word2] = word1
                else:
                    preferred[word1] = word2

        return preferred

    # Helper methods for tone analysis

    def _analyze_formality(self, text: str, total_words: int) -> float:
        """Analyze formality level of text."""
        formal_indicators = [
            'furthermore', 'moreover', 'consequently', 'therefore', 'however',
            'nevertheless', 'additionally', 'specifically', 'particularly',
            'subsequently', 'accordingly', 'thus', 'hence', 'whereas'
        ]

        informal_indicators = [
            "i'm", "you're", "we're", "they're", "don't", "won't", "can't",
            "shouldn't", "wouldn't", "couldn't", 'yeah', 'okay', 'ok',
            'awesome', 'cool', 'great', 'super', 'really', 'pretty',
            'kinda', 'sorta', 'gonna', 'wanna'
        ]

        text_lower = text.lower()

        formal_count = sum(text_lower.count(word) for word in formal_indicators)
        informal_count = sum(text_lower.count(word) for word in informal_indicators)

        # Normalize by total words
        formal_score = formal_count / total_words * 1000 if total_words > 0 else 0
        informal_score = informal_count / total_words * 1000 if total_words > 0 else 0

        # Calculate formality level (0.0 = very informal, 1.0 = very formal)
        if formal_score + informal_score == 0:
            return 0.5  # Neutral

        return formal_score / (formal_score + informal_score)

    def _analyze_enthusiasm(self, text: str, total_words: int) -> float:
        """Analyze enthusiasm level of text."""
        enthusiasm_indicators = [
            'amazing', 'awesome', 'fantastic', 'incredible', 'wonderful',
            'excellent', 'brilliant', 'outstanding', 'remarkable', 'superb',
            'love', 'excited', 'thrilled', 'delighted', 'passionate',
            'definitely', 'absolutely', 'certainly', 'totally', 'completely'
        ]

        text_lower = text.lower()
        enthusiasm_count = sum(text_lower.count(word) for word in enthusiasm_indicators)

        # Add exclamation marks as enthusiasm indicators
        enthusiasm_count += text.count('!')

        # Normalize and cap at reasonable level
        enthusiasm_score = enthusiasm_count / total_words * 1000 if total_words > 0 else 0
        return min(enthusiasm_score, 1.0)

    def _analyze_confidence(self, text: str, total_words: int) -> float:
        """Analyze confidence level of text."""
        confident_indicators = [
            'will', 'must', 'should', 'definitely', 'certainly', 'clearly',
            'obviously', 'undoubtedly', 'surely', 'always', 'never',
            'proven', 'guaranteed', 'ensure', 'confirm', 'establish'
        ]

        uncertain_indicators = [
            'might', 'maybe', 'perhaps', 'possibly', 'probably', 'seems',
            'appears', 'suggests', 'indicates', 'could', 'may', 'think',
            'believe', 'assume', 'suppose', 'guess', 'unsure', 'uncertain'
        ]

        text_lower = text.lower()

        confident_count = sum(text_lower.count(word) for word in confident_indicators)
        uncertain_count = sum(text_lower.count(word) for word in uncertain_indicators)

        # Normalize by total words
        confident_score = confident_count / total_words * 1000 if total_words > 0 else 0
        uncertain_score = uncertain_count / total_words * 1000 if total_words > 0 else 0

        # Calculate confidence level
        if confident_score + uncertain_score == 0:
            return 0.5  # Neutral

        return confident_score / (confident_score + uncertain_score)

    def _analyze_humor(self, text: str, total_words: int) -> float:
        """Analyze humor usage in text."""
        humor_indicators = [
            'lol', 'haha', 'funny', 'hilarious', 'joke', 'kidding',
            'seriously', 'ironically', 'surprisingly', 'awkward',
            'weird', 'strange', 'bizarre', 'ridiculous', 'silly'
        ]

        text_lower = text.lower()
        humor_count = sum(text_lower.count(word) for word in humor_indicators)

        # Look for emoticons and emoji patterns
        emoticon_patterns = [':)', ':(', ':D', ':P', ';)', ':-)', ':-(']
        for pattern in emoticon_patterns:
            humor_count += text.count(pattern)

        # Normalize
        humor_score = humor_count / total_words * 1000 if total_words > 0 else 0
        return min(humor_score, 1.0)

    def _detect_personal_anecdotes(self, text: str) -> bool:
        """Detect if text contains personal anecdotes."""
        personal_indicators = [
            'i was', 'i had', 'i did', 'i went', 'i saw', 'i found',
            'my experience', 'when i', 'i remember', 'i realized',
            'i discovered', 'i learned', 'i decided', 'i thought',
            'in my case', 'for me', 'personally'
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in personal_indicators)

    # Helper methods for structure analysis

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # Simple sentence splitting on periods, exclamations, and questions
        sentences = re.split(r'[.!?]+', text)

        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)

        return cleaned_sentences

    def _analyze_paragraph_preference(self, posts: List[BlogPost]) -> str:
        """Analyze paragraph length preferences."""
        paragraph_lengths = []

        for post in posts:
            paragraphs = post.content.split('\n\n')
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if paragraph and not paragraph.startswith('#'):  # Skip headers
                    word_count = len(paragraph.split())
                    if word_count > 5:  # Filter out very short paragraphs
                        paragraph_lengths.append(word_count)

        if not paragraph_lengths:
            return "medium"

        avg_length = sum(paragraph_lengths) / len(paragraph_lengths)

        if avg_length < 30:
            return "short"
        elif avg_length > 80:
            return "long"
        else:
            return "medium"

    def _analyze_list_usage(self, posts: List[BlogPost]) -> float:
        """Analyze frequency of list usage."""
        total_content_length = 0
        list_count = 0

        for post in posts:
            content = post.content
            total_content_length += len(content)

            # Count markdown lists
            list_count += len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE))
            list_count += len(re.findall(r'^\s*\d+\.\s', content, re.MULTILINE))

        # Return lists per 1000 characters
        return (list_count / total_content_length * 1000) if total_content_length > 0 else 0.0

    def _analyze_code_block_usage(self, posts: List[BlogPost]) -> float:
        """Analyze frequency of code block usage."""
        total_content_length = 0
        code_block_count = 0

        for post in posts:
            content = post.content
            total_content_length += len(content)

            # Count code blocks
            code_block_count += len(re.findall(r'```', content)) // 2  # Pairs of ```
            code_block_count += len(re.findall(r'`[^`\n]+`', content))  # Inline code

        # Return code blocks per 1000 characters
        return (code_block_count / total_content_length * 1000) if total_content_length > 0 else 0.0

    def _analyze_header_patterns(self, posts: List[BlogPost]) -> List[str]:
        """Analyze header usage patterns."""
        header_patterns = []

        for post in posts:
            headers = re.findall(r'^(#{1,6})\s+(.+)$', post.content, re.MULTILINE)
            for level, text in headers:
                pattern = f"H{len(level)}"
                header_patterns.append(pattern)

        # Return most common header patterns
        pattern_counter = Counter(header_patterns)
        return [pattern for pattern, _ in pattern_counter.most_common(10)]

    def _identify_transitions(self, posts: List[BlogPost]) -> List[str]:
        """Identify preferred transition phrases."""
        transition_patterns = [
            r'\b(however|nevertheless|furthermore|moreover|additionally)\b',
            r'\b(first|second|third|finally|lastly)\b',
            r'\b(next|then|after|before|meanwhile)\b',
            r'\b(in conclusion|to summarize|overall)\b',
            r'\b(for example|for instance|such as)\b',
            r'\b(on the other hand|in contrast|similarly)\b'
        ]

        transitions = []
        combined_text = ' '.join(post.content for post in posts)

        for pattern in transition_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            transitions.extend([match.lower() for match in matches])

        # Return most common transitions
        transition_counter = Counter(transitions)
        return [transition for transition, _ in transition_counter.most_common(10)]

    # Helper methods for emoji analysis

    def _extract_emojis(self, text: str) -> List[str]:
        """Extract emojis from text using Unicode ranges."""
        # Unicode ranges for emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        return emoji_pattern.findall(text)

    def _analyze_emoji_placement(self, content: List[str]) -> str:
        """Analyze where emojis are typically placed."""
        placement_scores = {"start": 0, "middle": 0, "end": 0}

        for text in content:
            sentences = self._extract_sentences(text)
            for sentence in sentences:
                emojis = self._extract_emojis(sentence)
                if emojis:
                    sentence_length = len(sentence)
                    for emoji in emojis:
                        emoji_pos = sentence.find(emoji)
                        relative_pos = emoji_pos / sentence_length if sentence_length > 0 else 0

                        if relative_pos < 0.2:
                            placement_scores["start"] += 1
                        elif relative_pos > 0.8:
                            placement_scores["end"] += 1
                        else:
                            placement_scores["middle"] += 1

        if not any(placement_scores.values()):
            return "end"  # Default

        return max(placement_scores, key=placement_scores.get)

    def _detect_technical_emoji_usage(self, emojis: List[str]) -> bool:
        """Detect if technical emojis are used."""
        technical_emojis = {
            '💻', '🖥️', '⌨️', '🖱️', '💾', '💿', '📀', '🔧', '⚙️', '🔩',
            '🔨', '⚡', '🔋', '🔌', '💡', '🔍', '📊', '📈', '📉', '📋',
            '📝', '📄', '📃', '📑', '🗂️', '📁', '📂', '🗃️', '🗄️'
        }

        return any(emoji in technical_emojis for emoji in emojis)

    def update_style_profile(self, existing_profile_path: str, posts_dir: str, notebooks_dir: str) -> StyleProfile:
        """
        Update existing style profile with new content.

        Args:
            existing_profile_path: Path to existing style profile
            posts_dir: Directory containing markdown blog posts
            notebooks_dir: Directory containing Jupyter notebook posts

        Returns:
            Updated StyleProfile object

        Raises:
            StyleAnalysisError: If update fails
        """
        try:
            # Try to load existing profile
            existing_profile = None
            if Path(existing_profile_path).exists():
                try:
                    existing_profile = self.load_style_profile(existing_profile_path)
                except StyleAnalysisError:
                    # If loading fails, create new profile
                    pass

            # Build new profile from current content
            new_profile = self.build_style_profile(posts_dir, notebooks_dir)

            # If no existing profile, return new one
            if existing_profile is None:
                return new_profile

            # Merge profiles with weighted average based on post count
            merged_profile = self._merge_style_profiles(existing_profile, new_profile)

            return merged_profile

        except Exception as e:
            if isinstance(e, StyleAnalysisError):
                raise
            raise StyleAnalysisError(f"Failed to update style profile: {e}")

    def _merge_style_profiles(self, existing: StyleProfile, new: StyleProfile) -> StyleProfile:
        """
        Merge two style profiles using weighted averaging.

        Args:
            existing: Existing style profile
            new: New style profile

        Returns:
            Merged StyleProfile
        """
        # Calculate weights based on post counts
        existing_weight = existing.posts_analyzed
        new_weight = new.posts_analyzed
        total_weight = existing_weight + new_weight

        if total_weight == 0:
            return new

        existing_ratio = existing_weight / total_weight
        new_ratio = new_weight / total_weight

        # Merge vocabulary patterns
        merged_vocab = VocabularyProfile(
            common_words=self._merge_word_lists(
                existing.vocabulary_patterns.common_words,
                new.vocabulary_patterns.common_words
            ),
            technical_terms=self._merge_word_lists(
                existing.vocabulary_patterns.technical_terms,
                new.vocabulary_patterns.technical_terms
            ),
            word_frequency=self._merge_word_frequencies(
                existing.vocabulary_patterns.word_frequency,
                new.vocabulary_patterns.word_frequency,
                existing_ratio,
                new_ratio
            ),
            average_word_length=(
                existing.vocabulary_patterns.average_word_length * existing_ratio +
                new.vocabulary_patterns.average_word_length * new_ratio
            ),
            vocabulary_diversity=(
                existing.vocabulary_patterns.vocabulary_diversity * existing_ratio +
                new.vocabulary_patterns.vocabulary_diversity * new_ratio
            ),
            preferred_synonyms={
                **existing.vocabulary_patterns.preferred_synonyms,
                **new.vocabulary_patterns.preferred_synonyms
            }
        )

        # Merge tone indicators
        merged_tone = ToneProfile(
            formality_level=(
                existing.tone_indicators.formality_level * existing_ratio +
                new.tone_indicators.formality_level * new_ratio
            ),
            enthusiasm_level=(
                existing.tone_indicators.enthusiasm_level * existing_ratio +
                new.tone_indicators.enthusiasm_level * new_ratio
            ),
            confidence_level=(
                existing.tone_indicators.confidence_level * existing_ratio +
                new.tone_indicators.confidence_level * new_ratio
            ),
            humor_usage=(
                existing.tone_indicators.humor_usage * existing_ratio +
                new.tone_indicators.humor_usage * new_ratio
            ),
            personal_anecdotes=(
                existing.tone_indicators.personal_anecdotes or
                new.tone_indicators.personal_anecdotes
            ),
            question_frequency=(
                existing.tone_indicators.question_frequency * existing_ratio +
                new.tone_indicators.question_frequency * new_ratio
            ),
            exclamation_frequency=(
                existing.tone_indicators.exclamation_frequency * existing_ratio +
                new.tone_indicators.exclamation_frequency * new_ratio
            )
        )

        # Merge structure profiles
        merged_structure = StructureProfile(
            average_sentence_length=(
                existing.content_structures.average_sentence_length * existing_ratio +
                new.content_structures.average_sentence_length * new_ratio
            ),
            paragraph_length_preference=new.content_structures.paragraph_length_preference,  # Use latest
            list_usage_frequency=(
                existing.content_structures.list_usage_frequency * existing_ratio +
                new.content_structures.list_usage_frequency * new_ratio
            ),
            code_block_frequency=(
                existing.content_structures.code_block_frequency * existing_ratio +
                new.content_structures.code_block_frequency * new_ratio
            ),
            header_usage_patterns=self._merge_word_lists(
                existing.content_structures.header_usage_patterns,
                new.content_structures.header_usage_patterns
            ),
            preferred_transitions=self._merge_word_lists(
                existing.content_structures.preferred_transitions,
                new.content_structures.preferred_transitions
            )
        )

        # Merge emoji profiles
        merged_emoji = EmojiProfile(
            emoji_frequency=(
                existing.emoji_usage.emoji_frequency * existing_ratio +
                new.emoji_usage.emoji_frequency * new_ratio
            ),
            common_emojis=self._merge_word_lists(
                existing.emoji_usage.common_emojis,
                new.emoji_usage.common_emojis
            ),
            emoji_placement=new.emoji_usage.emoji_placement,  # Use latest
            technical_emoji_usage=(
                existing.emoji_usage.technical_emoji_usage or
                new.emoji_usage.technical_emoji_usage
            )
        )

        # Create merged profile
        return StyleProfile(
            vocabulary_patterns=merged_vocab,
            tone_indicators=merged_tone,
            content_structures=merged_structure,
            emoji_usage=merged_emoji,
            created_at=datetime.now(),
            version="1.0.0",
            posts_analyzed=total_weight
        )

    def _merge_word_lists(self, list1: List[str], list2: List[str]) -> List[str]:
        """Merge two word lists, preserving order and removing duplicates."""
        seen = set()
        merged = []

        # Add from first list
        for word in list1:
            if word not in seen:
                merged.append(word)
                seen.add(word)

        # Add from second list
        for word in list2:
            if word not in seen:
                merged.append(word)
                seen.add(word)

        return merged

    def _merge_word_frequencies(self, freq1: Dict[str, int], freq2: Dict[str, int],
                               weight1: float, weight2: float) -> Dict[str, int]:
        """Merge word frequency dictionaries with weights."""
        merged = {}
        all_words = set(freq1.keys()) | set(freq2.keys())

        for word in all_words:
            count1 = freq1.get(word, 0)
            count2 = freq2.get(word, 0)
            merged_count = int(count1 * weight1 + count2 * weight2)
            if merged_count > 0:
                merged[word] = merged_count

        return merged

    def validate_style_profile(self, profile: StyleProfile) -> bool:
        """
        Validate style profile data integrity.

        Args:
            profile: StyleProfile to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not isinstance(profile.posts_analyzed, int) or profile.posts_analyzed < 0:
                return False

            if not isinstance(profile.version, str) or not profile.version:
                return False

            # Validate vocabulary patterns
            vocab = profile.vocabulary_patterns
            if not isinstance(vocab.common_words, list):
                return False

            if not isinstance(vocab.technical_terms, list):
                return False

            if not isinstance(vocab.word_frequency, dict):
                return False

            if not (0.0 <= vocab.vocabulary_diversity <= 1.0):
                return False

            # Validate tone indicators
            tone = profile.tone_indicators
            if not (0.0 <= tone.formality_level <= 1.0):
                return False

            if not (0.0 <= tone.enthusiasm_level <= 1.0):
                return False

            if not (0.0 <= tone.confidence_level <= 1.0):
                return False

            # Validate structure profile
            structure = profile.content_structures
            if structure.average_sentence_length < 0:
                return False

            if structure.paragraph_length_preference not in ["short", "medium", "long"]:
                return False

            # Validate emoji profile
            emoji = profile.emoji_usage
            if emoji.emoji_frequency < 0:
                return False

            if emoji.emoji_placement not in ["start", "middle", "end", "mixed"]:
                return False

            return True

        except Exception:
            return False