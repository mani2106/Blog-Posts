"""
AI orchestration and model management for the Tweet Thread Generator.

This module manages multiple AI model calls with different specializations,
handles OpenRouter API integration, and coordinates content generation workflow.
"""

from typing import List, Dict, Any, Optional
import httpx
import asyncio
import json
from datetime import datetime
import time
import random

from models import (
    BlogPost, StyleProfile, ThreadPlan, Tweet, ThreadData,
    ValidationResult, HookType
)
from exceptions import AIGenerationError, OpenRouterAPIError
from utils import truncate_text
from logger import get_logger, OperationType
from metrics import get_metrics_collector, ErrorCategory


class AIOrchestrator:
    """Orchestrates AI model calls for tweet thread generation."""

    def __init__(self, api_key: str, planning_model: str, creative_model: str, verification_model: str):
        """
        Initialize AI orchestrator.

        Args:
            api_key: OpenRouter API key
            planning_model: Model for thread structure planning
            creative_model: Model for creative content generation
            verification_model: Model for content verification
        """
        self.api_key = api_key
        self.planning_model = planning_model
        self.creative_model = creative_model
        self.verification_model = verification_model
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = get_logger()
        self.metrics = get_metrics_collector()

    def generate_thread_plan(self, post: BlogPost, style_profile: StyleProfile) -> ThreadPlan:
        """
        Generate thread structure plan using planning model.

        Args:
            post: BlogPost to create thread for
            style_profile: Author's writing style profile

        Returns:
            ThreadPlan with structure and strategy

        Raises:
            AIGenerationError: If thread planning fails
        """
        try:
            with self.logger.operation_context(OperationType.AI_GENERATION,
                                             operation="thread_planning",
                                             post_slug=post.slug,
                                             model_used=self.planning_model) as op_metrics:

                self.logger.info("Generating thread plan",
                               post_title=post.title,
                               post_slug=post.slug,
                               model=self.planning_model)

                # Build planning prompt
                prompt = self._build_planning_prompt(post, style_profile)
                op_metrics.characters_processed = len(prompt)

                # Get model configuration for planning
                model, max_tokens, temperature = self._get_model_config("planning")

                # Make API call with timing
                start_time = time.time()
                response = self._call_openrouter_sync(model, prompt, max_tokens, temperature)
                response_time_ms = (time.time() - start_time) * 1000

                op_metrics.api_calls_made = 1

                # Extract token usage from response
                usage = response.get('usage', {})
                tokens_used = usage.get('total_tokens', 0)

                # Log API call metrics
                self.metrics.record_api_call(
                    endpoint=f"{self.base_url}/chat/completions",
                    method="POST",
                    response_time_ms=response_time_ms,
                    status_code=200,
                    tokens_used=tokens_used,
                    success=True
                )

                content = self._extract_content_from_response(response)

                # Parse the structured response
                plan_data = self._parse_thread_plan_response(content)

                self.logger.info("Thread plan generated successfully",
                               post_slug=post.slug,
                               hook_type=plan_data['hook_type'],
                               estimated_tweets=plan_data['estimated_tweets'],
                               response_time_ms=response_time_ms)

                return ThreadPlan(
                    hook_type=HookType(plan_data["hook_type"]),
                    main_points=plan_data["main_points"],
                    call_to_action=plan_data["call_to_action"],
                    estimated_tweets=plan_data["estimated_tweets"],
                    engagement_strategy=plan_data["engagement_strategy"]
                )

        except Exception as e:
            self.metrics.record_error(
                error_category=ErrorCategory.API_ERROR if isinstance(e, OpenRouterAPIError) else ErrorCategory.CONTENT_ERROR,
                error=e,
                operation_type=OperationType.AI_GENERATION,
                post_slug=post.slug,
                api_endpoint=f"{self.base_url}/chat/completions"
            )

            self.logger.error("Thread planning failed",
                            post_slug=post.slug,
                            post_title=post.title,
                            error=e)

            if isinstance(e, (OpenRouterAPIError, AIGenerationError)):
                raise
            raise AIGenerationError(f"Thread planning failed: {str(e)}", details={"post_title": post.title})

    def generate_hook_variations(self, post: BlogPost, style_profile: StyleProfile, count: int = 3) -> List[str]:
        """
        Generate multiple hook variations for thread opening.

        Args:
            post: BlogPost to create hooks for
            style_profile: Author's writing style profile
            count: Number of hook variations to generate

        Returns:
            List of hook variations

        Raises:
            AIGenerationError: If hook generation fails
        """
        try:
            with self.logger.operation_context(OperationType.AI_GENERATION,
                                             operation="hook_generation",
                                             post_slug=post.slug,
                                             model_used=self.creative_model) as op_metrics:

                self.logger.info("Generating hook variations",
                               post_title=post.title,
                               post_slug=post.slug,
                               hook_count=count,
                               model=self.creative_model)

                # Build hook generation prompt
                prompt = self._build_hook_generation_prompt(post, style_profile, count)
                op_metrics.characters_processed = len(prompt)

                # Get model configuration for creative tasks
                model, max_tokens, temperature = self._get_model_config("creative")

                # Make API call with timing
                start_time = time.time()
                response = self._call_openrouter_sync(model, prompt, max_tokens, temperature)
                response_time_ms = (time.time() - start_time) * 1000

                op_metrics.api_calls_made = 1

                # Extract token usage from response
                usage = response.get('usage', {})
                tokens_used = usage.get('total_tokens', 0)

                # Log API call metrics
                self.metrics.record_api_call(
                    endpoint=f"{self.base_url}/chat/completions",
                    method="POST",
                    response_time_ms=response_time_ms,
                    status_code=200,
                    tokens_used=tokens_used,
                    success=True
                )

                content = self._extract_content_from_response(response)

                # Parse hook variations from response
                hooks = self._parse_hook_variations_response(content)

            # Validate and truncate hooks to fit Twitter character limits
            validated_hooks = []
            for hook in hooks[:count]:  # Ensure we don't exceed requested count
                # Reserve space for thread indicator and URL
                max_hook_length = 240  # Leave room for " (1/n)" and URL
                if len(hook) > max_hook_length:
                    hook = truncate_text(hook, max_hook_length)
                validated_hooks.append(hook)

            self.logger.info(f"Generated {len(validated_hooks)} hook variations successfully")
            return validated_hooks

        except Exception as e:
            self.logger.error(f"Hook generation failed: {str(e)}")
            if isinstance(e, (OpenRouterAPIError, AIGenerationError)):
                raise
            raise AIGenerationError(f"Hook generation failed: {str(e)}", details={"post_title": post.title})

    def generate_thread_content(self, plan: ThreadPlan, post: BlogPost, style_profile: StyleProfile) -> List[Tweet]:
        """
        Generate tweet thread content based on plan.

        Args:
            plan: ThreadPlan with structure
            post: BlogPost source content
            style_profile: Author's writing style profile

        Returns:
            List of Tweet objects

        Raises:
            AIGenerationError: If content generation fails
        """
        try:
            self.logger.info(f"Generating thread content for post: {post.title}")

            # Build content generation prompt
            prompt = self._build_content_generation_prompt(plan, post, style_profile)

            # Get model configuration for creative tasks
            model, max_tokens, temperature = self._get_model_config("creative")

            # Make API call
            response = self._call_openrouter_sync(model, prompt, max_tokens, temperature)
            content = self._extract_content_from_response(response)

            # Parse thread content from response
            tweet_contents = self._parse_thread_content_response(content)

            # Create Tweet objects with validation
            tweets = []
            for i, tweet_content in enumerate(tweet_contents):
                # Validate character count (reserve space for thread indicators)
                max_length = 260 if i == 0 else 275  # First tweet needs space for URL, increased limits
                if len(tweet_content) > max_length:
                    tweet_content = truncate_text(tweet_content, max_length)

                tweet = Tweet(
                    content=tweet_content,
                    character_count=len(tweet_content),
                    position=i + 1,
                    hook_type=plan.hook_type if i == 0 else None
                )
                tweets.append(tweet)

            self.logger.info(f"Generated {len(tweets)} tweets successfully")
            return tweets

        except Exception as e:
            self.logger.error(f"Thread content generation failed: {str(e)}")
            if isinstance(e, (OpenRouterAPIError, AIGenerationError)):
                raise
            raise AIGenerationError(f"Thread content generation failed: {str(e)}", details={"post_title": post.title})

    def verify_content_quality(self, tweets: List[Tweet], style_profile: StyleProfile) -> ValidationResult:
        """
        Verify content quality using verification model.

        Args:
            tweets: List of tweets to verify
            style_profile: Author's writing style profile

        Returns:
            ValidationResult with quality assessment

        Raises:
            AIGenerationError: If verification fails
        """
        try:
            self.logger.info(f"Verifying content quality for {len(tweets)} tweets")

            # Build verification prompt
            prompt = self._build_verification_prompt(tweets, style_profile)

            # Get model configuration for verification
            model, max_tokens, temperature = self._get_model_config("verification")

            # Make API call
            response = self._call_openrouter_sync(model, prompt, max_tokens, temperature)
            content = self._extract_content_from_response(response)

            # Parse verification results
            verification_data = self._parse_verification_response(content)

            from models import ValidationStatus

            # Determine overall status
            if verification_data["has_errors"]:
                status = ValidationStatus.ERROR
            elif verification_data["has_warnings"]:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.VALID

            self.logger.info(f"Content verification completed: {status.value}")

            return ValidationResult(
                status=status,
                message=verification_data["summary"],
                details={
                    "quality_score": verification_data["quality_score"],
                    "style_consistency": verification_data["style_consistency"],
                    "engagement_potential": verification_data["engagement_potential"],
                    "issues": verification_data["issues"],
                    "suggestions": verification_data["suggestions"]
                }
            )

        except Exception as e:
            self.logger.error(f"Content verification failed: {str(e)}")
            if isinstance(e, (OpenRouterAPIError, AIGenerationError)):
                raise

            # Return a warning result if verification fails
            from models import ValidationStatus
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Content verification failed: {str(e)}",
                details={"verification_error": str(e)}
            )

    def _parse_thread_plan_response(self, content: str) -> Dict[str, Any]:
        """Parse thread plan from AI response."""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                return json.loads(content)

            # Fallback: parse structured text response
            lines = content.strip().split('\n')
            plan_data = {
                "hook_type": "curiosity",
                "main_points": [],
                "call_to_action": "",
                "estimated_tweets": 5,
                "engagement_strategy": ""
            }

            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if "hook type:" in line.lower():
                    hook_type = line.split(':', 1)[1].strip().lower()
                    # Map common variations to our enum values
                    hook_mapping = {
                        "curiosity": "curiosity",
                        "question": "question",
                        "statistic": "statistic",
                        "story": "story",
                        "contrarian": "contrarian",
                        "value": "value_proposition"
                    }
                    for key, value in hook_mapping.items():
                        if key in hook_type:
                            plan_data["hook_type"] = value
                            break
                elif "main points:" in line.lower():
                    current_section = "main_points"
                elif "call to action:" in line.lower():
                    plan_data["call_to_action"] = line.split(':', 1)[1].strip()
                elif "estimated tweets:" in line.lower():
                    try:
                        plan_data["estimated_tweets"] = int(line.split(':', 1)[1].strip())
                    except ValueError:
                        pass
                elif "engagement strategy:" in line.lower():
                    plan_data["engagement_strategy"] = line.split(':', 1)[1].strip()
                elif current_section == "main_points" and (line.startswith('-') or line.startswith('•')):
                    plan_data["main_points"].append(line[1:].strip())

            return plan_data

        except Exception as e:
            self.logger.warning(f"Failed to parse thread plan response: {e}")
            # Return default plan
            return {
                "hook_type": "curiosity",
                "main_points": ["Key insight from the blog post"],
                "call_to_action": "What do you think?",
                "estimated_tweets": 5,
                "engagement_strategy": "Build curiosity and provide value"
            }

    def _parse_hook_variations_response(self, content: str) -> List[str]:
        """Parse hook variations from AI response."""
        try:
            # Try to parse as JSON array first
            if content.strip().startswith('['):
                return json.loads(content)

            # Fallback: parse numbered or bulleted list
            hooks = []
            lines = content.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Remove numbering or bullets
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    hook = line.split('.', 1)[1].strip()
                elif line.startswith(('-', '•', '*')):
                    hook = line[1:].strip()
                elif line.startswith('"') and line.endswith('"'):
                    hook = line[1:-1].strip()
                else:
                    hook = line

                if hook and len(hook) > 10:  # Filter out very short responses
                    hooks.append(hook)

            return hooks[:5]  # Limit to 5 hooks max

        except Exception as e:
            self.logger.warning(f"Failed to parse hook variations: {e}")
            return ["Here's something interesting about this topic..."]

    def _parse_thread_content_response(self, content: str) -> List[str]:
        """Parse thread content from AI response."""
        try:
            # Try to parse as JSON array first
            if content.strip().startswith('['):
                return json.loads(content)

            # Fallback: parse numbered tweets
            tweets = []
            lines = content.strip().split('\n')
            current_tweet = ""

            for line in lines:
                line = line.strip()
                if not line:
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                        current_tweet = ""
                    continue

                # Check if this is a new tweet (numbered)
                if line.startswith(('1/', '2/', '3/', '4/', '5/', '6/', '7/', '8/', '9/', '10/')):
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    # Remove the numbering
                    current_tweet = line.split('/', 1)[1].strip() if '/' in line else line
                elif line.startswith(('Tweet 1:', 'Tweet 2:', 'Tweet 3:')):
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    current_tweet = line.split(':', 1)[1].strip()
                else:
                    # Continue current tweet
                    if current_tweet:
                        current_tweet += " " + line
                    else:
                        current_tweet = line

            # Add the last tweet
            if current_tweet:
                tweets.append(current_tweet.strip())

            return tweets[:10]  # Limit to 10 tweets max

        except Exception as e:
            self.logger.warning(f"Failed to parse thread content: {e}")
            return ["This is an interesting topic worth exploring further."]

    def _parse_verification_response(self, content: str) -> Dict[str, Any]:
        """Parse verification results from AI response."""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                return json.loads(content)

            # Fallback: parse structured text
            verification_data = {
                "has_errors": False,
                "has_warnings": False,
                "quality_score": 0.8,
                "style_consistency": 0.8,
                "engagement_potential": 0.8,
                "issues": [],
                "suggestions": [],
                "summary": "Content appears to be of good quality"
            }

            lines = content.strip().split('\n')
            current_section = None

            for line in lines:
                line = line.strip().lower()
                if not line:
                    continue

                if "errors:" in line or "problems:" in line:
                    current_section = "issues"
                    if "no errors" not in line and "no problems" not in line:
                        verification_data["has_errors"] = True
                elif "warnings:" in line:
                    current_section = "warnings"
                    if "no warnings" not in line:
                        verification_data["has_warnings"] = True
                elif "suggestions:" in line or "recommendations:" in line:
                    current_section = "suggestions"
                elif "quality score:" in line:
                    try:
                        score = float(line.split(':')[1].strip().replace('%', '')) / 100
                        verification_data["quality_score"] = score
                    except ValueError:
                        pass
                elif current_section and (line.startswith('-') or line.startswith('•')):
                    item = line[1:].strip()
                    if current_section == "issues":
                        verification_data["issues"].append(item)
                    elif current_section == "warnings":
                        verification_data["issues"].append(f"Warning: {item}")
                        verification_data["has_warnings"] = True
                    elif current_section == "suggestions":
                        verification_data["suggestions"].append(item)

            return verification_data

        except Exception as e:
            self.logger.warning(f"Failed to parse verification response: {e}")
            return {
                "has_errors": False,
                "has_warnings": True,
                "quality_score": 0.7,
                "style_consistency": 0.7,
                "engagement_potential": 0.7,
                "issues": [],
                "suggestions": [],
                "summary": "Verification parsing failed, manual review recommended"
            }

    async def _call_openrouter_api(self, model: str, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Make API call to OpenRouter with retry logic and error handling.

        Args:
            model: Model identifier
            prompt: Prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            API response data

        Raises:
            OpenRouterAPIError: If API call fails after retries
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tweet-thread-generator",
            "X-Title": "Tweet Thread Generator"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    self.logger.info(f"Making OpenRouter API call (attempt {attempt + 1}/{max_retries})")
                    self.logger.debug(f"Model: {model}, Max tokens: {max_tokens}, Temperature: {temperature}")

                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )

                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", base_delay * (2 ** attempt)))
                        self.logger.warning(f"Rate limited. Waiting {retry_after} seconds before retry.")
                        await asyncio.sleep(retry_after)
                        continue

                    # Handle other HTTP errors
                    if response.status_code != 200:
                        error_detail = response.text
                        self.logger.error(f"OpenRouter API error {response.status_code}: {error_detail}")

                        if attempt == max_retries - 1:
                            raise OpenRouterAPIError(
                                f"API request failed with status {response.status_code}",
                                details={
                                    "status_code": response.status_code,
                                    "response": error_detail,
                                    "model": model
                                }
                            )

                        # Exponential backoff for server errors
                        if response.status_code >= 500:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                            self.logger.info(f"Server error, retrying in {delay:.2f} seconds")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            # Client errors shouldn't be retried
                            raise OpenRouterAPIError(
                                f"API request failed with status {response.status_code}",
                                details={
                                    "status_code": response.status_code,
                                    "response": error_detail,
                                    "model": model
                                }
                            )

                    # Parse successful response
                    try:
                        response_data = response.json()
                        self.logger.info("OpenRouter API call successful")
                        self.logger.debug(f"Response usage: {response_data.get('usage', {})}")
                        return response_data
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse API response as JSON: {e}")
                        if attempt == max_retries - 1:
                            raise OpenRouterAPIError(
                                "Failed to parse API response",
                                details={"json_error": str(e), "response": response.text}
                            )

            except httpx.TimeoutException:
                self.logger.warning(f"API request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    raise OpenRouterAPIError(
                        "API request timed out after multiple attempts",
                        details={"timeout": True, "model": model}
                    )

                # Exponential backoff for timeouts
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

            except httpx.RequestError as e:
                self.logger.error(f"Network error during API request: {e}")
                if attempt == max_retries - 1:
                    raise OpenRouterAPIError(
                        f"Network error: {str(e)}",
                        details={"network_error": str(e), "model": model}
                    )

                # Exponential backoff for network errors
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        raise OpenRouterAPIError(
            "Maximum retries exceeded",
            details={"max_retries": max_retries, "model": model}
        )

    def _call_openrouter_sync(self, model: str, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Synchronous wrapper for OpenRouter API calls.

        Args:
            model: Model identifier
            prompt: Prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            API response data

        Raises:
            OpenRouterAPIError: If API call fails
        """
        try:
            return asyncio.run(self._call_openrouter_api(model, prompt, max_tokens, temperature))
        except Exception as e:
            if isinstance(e, OpenRouterAPIError):
                raise
            raise OpenRouterAPIError(f"Unexpected error during API call: {str(e)}", details={"error": str(e)})

    def _extract_content_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract content from OpenRouter API response.

        Args:
            response: API response dictionary

        Returns:
            Generated content string

        Raises:
            OpenRouterAPIError: If response format is invalid
        """
        try:
            choices = response.get("choices", [])
            if not choices:
                raise OpenRouterAPIError("No choices in API response", details={"response": response})

            message = choices[0].get("message", {})
            content = message.get("content", "")

            if not content:
                raise OpenRouterAPIError("Empty content in API response", details={"response": response})

            return content.strip()

        except (KeyError, IndexError, TypeError) as e:
            raise OpenRouterAPIError(
                f"Invalid response format: {str(e)}",
                details={"response": response, "parse_error": str(e)}
            )

    def _get_model_config(self, task_type: str) -> tuple[str, int, float]:
        """
        Get model configuration for specific task type.

        Args:
            task_type: Type of task ('planning', 'creative', 'verification')

        Returns:
            Tuple of (model_name, max_tokens, temperature)
        """
        configs = {
            "planning": (self.planning_model, 800, 0.3),
            "creative": (self.creative_model, 1200, 0.8),
            "verification": (self.verification_model, 600, 0.2)
        }

        if task_type not in configs:
            self.logger.warning(f"Unknown task type '{task_type}', using planning model")
            task_type = "planning"

        model, max_tokens, temperature = configs[task_type]
        self.logger.debug(f"Using {task_type} config: model={model}, max_tokens={max_tokens}, temperature={temperature}")

        return model, max_tokens, temperature

    def test_api_connection(self) -> ValidationResult:
        """
        Test OpenRouter API connection and authentication.

        Returns:
            ValidationResult indicating connection status
        """
        try:
            test_prompt = "Hello, this is a test. Please respond with 'API connection successful'."
            response = self._call_openrouter_sync(
                model=self.planning_model,
                prompt=test_prompt,
                max_tokens=50,
                temperature=0.1
            )

            content = self._extract_content_from_response(response)

            from models import ValidationStatus
            return ValidationResult(
                status=ValidationStatus.VALID,
                message="OpenRouter API connection successful",
                details={"test_response": content}
            )

        except OpenRouterAPIError as e:
            from models import ValidationStatus
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"OpenRouter API connection failed: {e.message}",
                details=e.details,
                is_valid=False
            )
        except Exception as e:
            from models import ValidationStatus
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Unexpected error testing API: {str(e)}",
                details={"error": str(e)},
                is_valid=False
            )

    def _build_style_aware_prompt(self, base_prompt: str, style_profile: StyleProfile) -> str:
        """
        Build prompt that incorporates writing style profile.

        Args:
            base_prompt: Base prompt template
            style_profile: Author's writing style profile

        Returns:
            Style-aware prompt string
        """
        # Extract key style characteristics
        tone = style_profile.tone_indicators
        vocab = style_profile.vocabulary_patterns
        structure = style_profile.content_structures
        emoji = style_profile.emoji_usage

        # Build style context
        style_context = f"""
AUTHOR WRITING STYLE PROFILE:

Tone Characteristics:
- Formality Level: {self._describe_formality(tone.formality_level)}
- Enthusiasm: {self._describe_enthusiasm(tone.enthusiasm_level)}
- Confidence: {self._describe_confidence(tone.confidence_level)}
- Humor Usage: {self._describe_humor(tone.humor_usage)}
- Uses Personal Anecdotes: {"Yes" if tone.personal_anecdotes else "No"}

Vocabulary Patterns:
- Common Words: {', '.join(vocab.common_words[:10]) if vocab.common_words else "Standard vocabulary"}
- Technical Terms: {', '.join(vocab.technical_terms[:8]) if vocab.technical_terms else "Minimal technical jargon"}
- Average Word Length: {vocab.average_word_length:.1f} characters
- Vocabulary Diversity: {self._describe_diversity(vocab.vocabulary_diversity)}

Content Structure:
- Sentence Length: {self._describe_sentence_length(structure.average_sentence_length)}
- Paragraph Style: {structure.paragraph_length_preference}
- List Usage: {self._describe_frequency(structure.list_usage_frequency)}
- Preferred Transitions: {', '.join(structure.preferred_transitions[:5]) if structure.preferred_transitions else "Standard transitions"}

Emoji Usage:
- Frequency: {self._describe_frequency(emoji.emoji_frequency)}
- Common Emojis: {' '.join(emoji.common_emojis[:8]) if emoji.common_emojis else "Minimal emoji use"}
- Placement Style: {emoji.emoji_placement}

IMPORTANT: Match this exact writing style in your response. Use similar vocabulary, tone, and structural patterns.
"""

        return f"{style_context}\n\n{base_prompt}"

    def _describe_formality(self, level: float) -> str:
        """Convert formality level to description."""
        if level < 0.3:
            return "Very casual and conversational"
        elif level < 0.6:
            return "Moderately informal, approachable"
        elif level < 0.8:
            return "Professional but friendly"
        else:
            return "Formal and authoritative"

    def _describe_enthusiasm(self, level: float) -> str:
        """Convert enthusiasm level to description."""
        if level < 0.3:
            return "Calm and measured"
        elif level < 0.6:
            return "Moderately enthusiastic"
        elif level < 0.8:
            return "Energetic and passionate"
        else:
            return "Highly enthusiastic and excited"

    def _describe_confidence(self, level: float) -> str:
        """Convert confidence level to description."""
        if level < 0.3:
            return "Humble and questioning"
        elif level < 0.6:
            return "Balanced confidence"
        elif level < 0.8:
            return "Confident and assertive"
        else:
            return "Very confident and authoritative"

    def _describe_humor(self, level: float) -> str:
        """Convert humor usage to description."""
        if level < 0.2:
            return "Serious, minimal humor"
        elif level < 0.5:
            return "Occasional light humor"
        elif level < 0.8:
            return "Regular use of humor"
        else:
            return "Frequent humor and wit"

    def _describe_diversity(self, level: float) -> str:
        """Convert vocabulary diversity to description."""
        if level < 0.3:
            return "Simple, repetitive vocabulary"
        elif level < 0.6:
            return "Moderate vocabulary range"
        elif level < 0.8:
            return "Rich and varied vocabulary"
        else:
            return "Extensive, sophisticated vocabulary"

    def _describe_sentence_length(self, length: float) -> str:
        """Convert sentence length to description."""
        if length < 10:
            return "Very short, punchy sentences"
        elif length < 15:
            return "Short to medium sentences"
        elif length < 20:
            return "Medium length sentences"
        else:
            return "Long, detailed sentences"

    def _describe_frequency(self, freq: float) -> str:
        """Convert frequency to description."""
        if freq < 0.2:
            return "Rarely used"
        elif freq < 0.5:
            return "Occasionally used"
        elif freq < 0.8:
            return "Frequently used"
        else:
            return "Very frequently used"

    def _build_planning_prompt(self, post: BlogPost, style_profile: StyleProfile) -> str:
        """Build prompt for thread structure planning."""
        base_prompt = f"""
You are an expert social media strategist specializing in Twitter thread creation. Your task is to analyze a blog post and create a strategic plan for converting it into an engaging Twitter thread.

BLOG POST TO ANALYZE:
Title: {post.title}
Categories: {', '.join(post.categories)}
Summary: {post.summary or 'No summary provided'}
Content Preview: {truncate_text(post.content, 1000)}

TASK: Create a strategic thread plan that will maximize engagement and effectively communicate the blog post's key insights.

Please respond with a JSON object containing:
{{
    "hook_type": "curiosity|question|statistic|story|contrarian|value_proposition",
    "main_points": ["point 1", "point 2", "point 3"],
    "call_to_action": "engaging question or request",
    "estimated_tweets": 5-8,
    "engagement_strategy": "brief description of approach"
}}

Consider:
1. What hook type would work best for this content and audience?
2. What are the 3-5 most important points to communicate?
3. How can we structure this for maximum engagement?
4. What call-to-action would encourage interaction?

Focus on creating a plan that matches the author's established voice and maximizes the content's viral potential.
"""
        return self._build_style_aware_prompt(base_prompt, style_profile)

    def _build_hook_generation_prompt(self, post: BlogPost, style_profile: StyleProfile, count: int) -> str:
        """Build prompt for hook generation."""
        content_type = self._determine_content_type(post)

        base_prompt = f"""
You are a viral content creator specializing in Twitter thread hooks. Your task is to create {count} different engaging opening tweets for a blog post.

BLOG POST DETAILS:
Title: {post.title}
Categories: {', '.join(post.categories)}
Content Type: {content_type}
Summary: {post.summary or 'No summary provided'}
Key Content: {truncate_text(post.content, 800)}

TASK: Create {count} different hook variations that will stop people from scrolling and make them want to read the entire thread.

Hook Types to Consider:
1. CURIOSITY GAP: "What if I told you..." / "The secret that..."
2. CONTRARIAN: "Everyone says X, but here's why they're wrong..."
3. STATISTIC: "X% of people don't know this..."
4. STORY: "Last week something happened that changed everything..."
5. QUESTION: "Have you ever wondered why..."
6. VALUE PROPOSITION: "Here's how to X in Y minutes..."

Requirements:
- Each hook must be under 240 characters (leave room for thread numbering and URL)
- Match the author's established tone and voice
- Create genuine curiosity without being clickbait
- Be specific to this blog post's content
- Avoid generic or overused phrases

Please respond with a JSON array of {count} hook strings:
["hook 1", "hook 2", "hook 3"]

Make each hook unique and compelling while staying authentic to the content.
"""
        return self._build_style_aware_prompt(base_prompt, style_profile)

    def _build_content_generation_prompt(self, plan: ThreadPlan, post: BlogPost, style_profile: StyleProfile) -> str:
        """Build prompt for thread content generation."""
        base_prompt = f"""
You are an expert Twitter thread creator. Your task is to convert a blog post into an engaging Twitter thread based on the provided strategic plan.

STRATEGIC PLAN:
Hook Type: {plan.hook_type.value}
Main Points: {', '.join(plan.main_points)}
Call to Action: {plan.call_to_action}
Estimated Tweets: {plan.estimated_tweets}
Strategy: {plan.engagement_strategy}

BLOG POST CONTENT:
Title: {post.title}
Categories: {', '.join(post.categories)}
URL: {post.canonical_url}
Content: {truncate_text(post.content, 1500)}

TASK: Create a Twitter thread of {plan.estimated_tweets} tweets that follows the strategic plan and maximizes engagement.

Thread Structure Requirements:
1. OPENING TWEET: Use the {plan.hook_type.value} hook type to grab attention
2. MIDDLE TWEETS: Cover each main point with valuable insights
3. CLOSING TWEET: Include the call-to-action and encourage engagement

Technical Requirements:
- First tweet: Max 240 characters (needs space for URL and thread indicator)
- Other tweets: Max 270 characters (needs space for thread indicator)
- Include the blog post URL in the first tweet
- Use thread numbering (1/n, 2/n, etc.)
- Maintain consistent voice throughout
- Include strategic line breaks for readability

Content Guidelines:
- Provide genuine value in each tweet
- Use specific examples and insights from the blog post
- Create natural flow between tweets
- End with strong call-to-action
- Match the author's established writing style

Please respond with a JSON array of tweet strings:
["1/{plan.estimated_tweets} [opening hook tweet with URL]", "2/{plan.estimated_tweets} [content tweet]", ...]

Focus on creating content that people will want to like, retweet, and reply to.
"""
        return self._build_style_aware_prompt(base_prompt, style_profile)

    def _build_verification_prompt(self, tweets: List[Tweet], style_profile: StyleProfile) -> str:
        """Build prompt for content verification."""
        tweet_contents = [f"Tweet {i+1}: {tweet.content}" for i, tweet in enumerate(tweets)]

        base_prompt = f"""
You are a content quality analyst specializing in social media. Your task is to evaluate a Twitter thread for quality, style consistency, and engagement potential.

TWITTER THREAD TO EVALUATE:
{chr(10).join(tweet_contents)}

EVALUATION CRITERIA:
1. STYLE CONSISTENCY: Does the thread match the author's established voice and tone?
2. ENGAGEMENT POTENTIAL: Will this thread generate likes, retweets, and replies?
3. CONTENT QUALITY: Is the information valuable and well-presented?
4. TECHNICAL COMPLIANCE: Are character limits and formatting correct?
5. AUTHENTICITY: Does it feel genuine rather than overly promotional?

Please provide a detailed evaluation in JSON format:
{{
    "has_errors": false,
    "has_warnings": false,
    "quality_score": 0.85,
    "style_consistency": 0.90,
    "engagement_potential": 0.80,
    "issues": ["any problems found"],
    "suggestions": ["improvement recommendations"],
    "summary": "overall assessment"
}}

Look for:
- Character count violations
- Inconsistent tone or voice
- Weak hooks or calls-to-action
- Missing engagement elements
- Factual accuracy concerns
- Overly promotional language
- Poor flow between tweets

Provide specific, actionable feedback for improvement.
"""
        return self._build_style_aware_prompt(base_prompt, style_profile)

    def _determine_content_type(self, post: BlogPost) -> str:
        """Determine content type based on post characteristics."""
        categories = [cat.lower() for cat in post.categories]
        title_lower = post.title.lower()
        content_lower = post.content.lower()

        # Check for tutorial/how-to content
        if any(word in title_lower for word in ['how to', 'guide', 'tutorial', 'step by step']):
            return "tutorial"
        if any(word in content_lower[:500] for word in ['step 1', 'first step', 'follow these']):
            return "tutorial"

        # Check for technical content
        if any(cat in categories for cat in ['programming', 'tech', 'development', 'coding']):
            return "technical"
        if any(word in content_lower[:500] for word in ['code', 'function', 'algorithm', 'api']):
            return "technical"

        # Check for personal/experience content
        if any(word in title_lower for word in ['my', 'i learned', 'experience', 'journey']):
            return "personal"
        if any(cat in categories for cat in ['personal', 'career', 'life']):
            return "personal"

        # Check for analysis/opinion content
        if any(word in title_lower for word in ['analysis', 'review', 'thoughts', 'opinion']):
            return "analysis"

        # Default to informational
        return "informational"

    def generate_thread(self, post: BlogPost, style_profile: StyleProfile) -> Optional[ThreadData]:
        """
        Generate a complete thread by orchestrating all generation steps.

        Args:
            post: Blog post to generate thread for
            style_profile: Author's writing style profile

        Returns:
            Complete ThreadData object or None if generation fails
        """
        try:
            # Step 1: Generate thread plan
            thread_plan = self.generate_thread_plan(post, style_profile)
            if not thread_plan:
                self.logger.error("Failed to generate thread plan")
                return None

            # Step 2: Generate hook variations
            hook_variations = self.generate_hook_variations(post, style_profile, count=3)
            if not hook_variations:
                self.logger.warning("Failed to generate hook variations, using default")
                hook_variations = ["Here's something interesting about this topic..."]

            # Step 3: Generate thread content
            tweets = self.generate_thread_content(thread_plan, post, style_profile)
            if not tweets:
                self.logger.error("Failed to generate thread content")
                return None

            # Step 4: Create ThreadData object
            thread_data = ThreadData(
                post_slug=post.slug,
                tweets=tweets,
                hook_variations=hook_variations,
                hashtags=[],  # Will be populated by engagement optimizer
                engagement_score=0.0,  # Will be calculated by engagement optimizer
                model_used=self.creative_model,
                style_profile_version=style_profile.version,
                thread_plan=thread_plan
            )

            self.logger.info(f"Successfully generated thread for post: {post.slug}")
            return thread_data

        except Exception as e:
            self.logger.error(f"Failed to generate thread for post {post.slug}: {e}")
            return None