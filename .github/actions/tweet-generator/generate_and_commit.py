#!/usr/bin/env python3
"""
Main entry point for the GitHub Action Tweet Thread Generator.

This script orchestrates the entire tweet generation workflow:
1. Load configuration from environment variables and YAML files
2. Detect changed blog posts
3. Analyze writing style
4. Generate tweet threads with AI
5. Create pull requests for review
6. Optionally auto-post to Twitter
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import ValidationStatus, GeneratorConfig
from config import ConfigManager
from utils import ensure_directory, is_github_actions_environment, get_repository_info
from logger import setup_logging, get_logger, OperationType
from metrics import setup_metrics_collection, get_metrics_collector
from monitoring import setup_monitoring, get_monitoring_dashboard, get_health_monitor


def create_directories(config: GeneratorConfig) -> None:
    """Create necessary directories if they don't exist."""
    directories = [
        config.generated_directory,
        config.posted_directory
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def set_github_actions_output(key: str, value: str) -> None:
    """Set GitHub Actions output variable."""
    if os.getenv("GITHUB_ACTIONS"):
        output_file = os.environ.get("GITHUB_OUTPUT")
        if output_file:
            with open(output_file, "a") as f:
                f.write(f"{key}={value}\n")


def set_github_actions_outputs(threads_generated: int, posts_processed: int, pr_created: bool) -> None:
    """Set all GitHub Actions output variables."""
    set_github_actions_output("threads_generated", str(threads_generated))
    set_github_actions_output("posts_processed", str(posts_processed))
    set_github_actions_output("pr_created", "true" if pr_created else "false")


def main() -> int:
    """Main execution function."""
    # Initialize logging, metrics, and monitoring
    logger = setup_logging()
    metrics, health_monitor, dashboard = setup_monitoring()

    logger.info("Starting GitHub Action Tweet Thread Generator")

    try:
        with logger.operation_context(OperationType.CONTENT_DETECTION, operation="initialization") as init_metrics:
            # Load configuration from environment and YAML files
            config = ConfigManager.load_config()
            logger.info("Configuration loaded",
                       openrouter_model=config.openrouter_model,
                       engagement_level=config.engagement_optimization_level.value,
                       dry_run_mode=config.dry_run_mode)

            # Validate environment
            env_validation = ConfigManager.validate_environment()
            if env_validation.status == ValidationStatus.ERROR:
                logger.error("Environment validation failed",
                           validation_message=env_validation.message)
                return 1
            elif env_validation.status == ValidationStatus.WARNING:
                logger.warning("Environment validation warnings",
                             validation_message=env_validation.message)

            # Validate configuration
            validation_result = config.validate()
            if validation_result.status == ValidationStatus.ERROR:
                logger.error("Configuration validation failed",
                           validation_message=validation_result.message)
                return 1
            elif validation_result.status == ValidationStatus.WARNING:
                logger.warning("Configuration validation warnings",
                             validation_message=validation_result.message)

            # Create necessary directories
            create_directories(config)
            logger.info("Necessary directories created")

            # Initialize GitHub Actions outputs
            set_github_actions_outputs(0, 0, False)

            if config.dry_run_mode:
                logger.info("Running in dry-run mode - no actual changes will be made")

            # Log environment information
            if is_github_actions_environment():
                repo_info = get_repository_info()
                logger.info("GitHub Actions environment detected",
                           repository=repo_info.get('repository', 'unknown'),
                           ref=repo_info.get('ref', 'unknown'),
                           sha=repo_info.get('sha', 'unknown')[:8],
                           actor=repo_info.get('actor', 'unknown'),
                           run_id=repo_info.get('run_id', 'unknown'))

            logger.info("Tweet thread generator initialization completed successfully")

        # Import workflow components
        from content_detector import ContentDetector
        from style_analyzer import StyleAnalyzer
        from ai_orchestrator import AIOrchestrator
        from engagement_optimizer import EngagementOptimizer
        from content_validator import ContentValidator
        from output_manager import OutputManager

        # Initialize components
        content_detector = ContentDetector(config.posts_directory, config.notebooks_directory)
        style_analyzer = StyleAnalyzer(min_posts=3)
        ai_orchestrator = AIOrchestrator(
            api_key=config.openrouter_api_key,
            planning_model=config.openrouter_model,
            creative_model=config.creative_model,
            verification_model=config.verification_model
        )
        engagement_optimizer = EngagementOptimizer(config.engagement_optimization_level)
        content_validator = ContentValidator()
        output_manager = OutputManager(config)

        # Execute workflow
        threads_generated = 0
        posts_processed = 0
        pr_created = False

        try:
            # Step 1: Detect changed blog posts
            with logger.operation_context(OperationType.CONTENT_DETECTION, operation="detect_posts") as detect_metrics:
                logger.info("Detecting changed blog posts...")
                changed_posts = content_detector.detect_changed_posts()
                posts_processed = len(changed_posts)

                detect_metrics.files_created = posts_processed
                metrics.increment_counter("posts_detected", posts_processed)

                if not changed_posts:
                    logger.info("No changed posts found that need processing")
                    return 0

                logger.info("Changed posts detected",
                           posts_count=posts_processed,
                           post_slugs=[post.slug for post in changed_posts])

            # Step 2: Build or update style profile
            with logger.operation_context(OperationType.STYLE_ANALYSIS, operation="build_profile") as style_metrics:
                logger.info("Analyzing writing style...")
                try:
                    style_profile = style_analyzer.build_style_profile(
                        config.posts_directory,
                        config.notebooks_directory
                    )

                    style_metrics.files_created = 1  # style profile file
                    metrics.record_content_generation(
                        OperationType.STYLE_ANALYSIS,
                        "style-profile",
                        "internal",
                        processing_time_ms=style_metrics.duration_ms or 0,
                        success=True
                    )

                    logger.info("Style profile analysis completed",
                               posts_analyzed=style_profile.posts_analyzed,
                               profile_version=style_profile.version)
                except Exception as e:
                    style_metrics.finish(success=False, error=e)
                    metrics.record_error(
                        error_category=metrics.ErrorCategory.CONTENT_ERROR,
                        error=e,
                        operation_type=OperationType.STYLE_ANALYSIS
                    )

                    logger.error("Style analysis failed - continuing with default profile", error=e)
                    # Create a minimal default style profile
                    from models import StyleProfile
                    style_profile = StyleProfile()
                    style_profile.posts_analyzed = 0

            # Step 3: Process each post
            for i, post in enumerate(changed_posts, 1):
                with logger.operation_context(OperationType.AI_GENERATION,
                                            post_slug=post.slug,
                                            model_used=config.openrouter_model) as post_metrics:

                    logger.info("Processing post",
                               post_number=f"{i}/{posts_processed}",
                               post_title=post.title,
                               post_slug=post.slug)

                    # Check if already posted
                    if output_manager.check_already_posted(post.slug):
                        logger.info("Post already posted - skipping", post_slug=post.slug)
                        continue

                    try:
                        # Generate thread plan
                        logger.info("Generating thread plan", post_slug=post.slug)
                        thread_plan = ai_orchestrator.generate_thread_plan(post, style_profile)
                        post_metrics.api_calls_made += 1

                        # Generate hook variations
                        logger.info("Generating hook variations",
                                   post_slug=post.slug,
                                   hook_count=config.hook_variations_count)
                        hook_variations = ai_orchestrator.generate_hook_variations(post, config.hook_variations_count)
                        post_metrics.api_calls_made += 1

                        # Generate thread content
                        logger.info("Generating thread content",
                                   post_slug=post.slug,
                                   estimated_tweets=getattr(thread_plan, 'estimated_tweets', 0))
                        tweets = ai_orchestrator.generate_thread_content(thread_plan)
                        post_metrics.api_calls_made += 1

                        # Apply engagement optimization
                        with logger.operation_context(OperationType.ENGAGEMENT_OPTIMIZATION,
                                                    post_slug=post.slug) as engagement_metrics:
                            logger.info("Applying engagement optimization",
                                       post_slug=post.slug,
                                       tweet_count=len(tweets))
                            optimized_tweets = []
                            for tweet in tweets:
                                optimized_tweet = engagement_optimizer.optimize_tweet_content(tweet.content, post)
                                optimized_tweets.append(optimized_tweet)

                            engagement_metrics.characters_processed = sum(len(tweet) for tweet in optimized_tweets)

                        # Create thread data
                        from models import ThreadData
                        thread = ThreadData(
                            post_slug=post.slug,
                            tweets=optimized_tweets,
                            hook_variations=hook_variations,
                            hashtags=engagement_optimizer.optimize_hashtags(post.content, post.categories),
                            model_used=config.openrouter_model,
                            style_profile_version=style_profile.version,
                            thread_plan=thread_plan
                        )

                        # Validate content
                        with logger.operation_context(OperationType.CONTENT_VALIDATION,
                                                    post_slug=post.slug) as validation_metrics:
                            logger.info("Validating thread content", post_slug=post.slug)
                            validation_result = content_validator.validate_thread(thread)

                            if not validation_result.is_valid:
                                validation_metrics.finish(success=False)
                                metrics.record_error(
                                    error_category=metrics.ErrorCategory.VALIDATION_ERROR,
                                    error=Exception(validation_result.message),
                                    operation_type=OperationType.CONTENT_VALIDATION,
                                    post_slug=post.slug
                                )
                                logger.error("Thread validation failed",
                                           post_slug=post.slug,
                                           validation_message=validation_result.message)
                                continue

                            logger.info("Thread validation passed", post_slug=post.slug)

                        # Save thread draft
                        draft_path = output_manager.save_thread_draft(thread)
                        post_metrics.files_created += 1
                        logger.info("Thread draft saved",
                                   post_slug=post.slug,
                                   draft_path=draft_path)

                        # Check if auto-posting should be attempted
                        should_auto_post, reason = output_manager.should_auto_post(post)

                        if should_auto_post:
                            with logger.operation_context(OperationType.AUTO_POSTING,
                                                        post_slug=post.slug) as posting_metrics:
                                logger.info("Attempting auto-post", post_slug=post.slug)

                                # Attempt auto-posting
                                post_result = output_manager.post_to_twitter(thread, post)
                                posting_metrics.api_calls_made += len(thread.tweets)

                                if post_result.success:
                                    posting_metrics.files_created += 1  # posted metadata file
                                    metrics.increment_counter("posts_auto_posted")
                                    logger.info("Auto-posting successful",
                                               post_slug=post.slug,
                                               tweet_count=len(post_result.tweet_ids),
                                               tweet_ids=post_result.tweet_ids)
                                else:
                                    posting_metrics.finish(success=False, error=Exception(post_result.error_message))
                                    metrics.record_error(
                                        error_category=metrics.ErrorCategory.API_ERROR,
                                        error=Exception(post_result.error_message),
                                        operation_type=OperationType.AUTO_POSTING,
                                        post_slug=post.slug
                                    )
                                    logger.warning("Auto-posting failed - creating PR",
                                                 post_slug=post.slug,
                                                 error_message=post_result.error_message)
                                    # Fall back to PR creation
                                    pr_url = output_manager.create_or_update_pr(thread, post)
                                    logger.info("PR created for manual review",
                                               post_slug=post.slug,
                                               pr_url=pr_url)
                                    pr_created = True
                        else:
                            logger.info("Skipping auto-post - creating PR",
                                       post_slug=post.slug,
                                       reason=reason)
                            # Create PR for manual review
                            pr_url = output_manager.create_or_update_pr(thread, post)
                            logger.info("PR created for manual review",
                                       post_slug=post.slug,
                                       pr_url=pr_url)
                            pr_created = True

                        # Record successful content generation
                        metrics.record_content_generation(
                            OperationType.AI_GENERATION,
                            post.slug,
                            config.openrouter_model,
                            input_characters=len(post.content),
                            output_characters=sum(len(tweet) for tweet in optimized_tweets),
                            processing_time_ms=post_metrics.duration_ms or 0,
                            tweets_generated=len(optimized_tweets),
                            hooks_generated=len(hook_variations),
                            success=True
                        )

                        threads_generated += 1
                        metrics.increment_counter("threads_generated")

                    except Exception as e:
                        post_metrics.finish(success=False, error=e)
                        metrics.record_error(
                            error_category=metrics.ErrorCategory.UNKNOWN_ERROR,
                            error=e,
                            operation_type=OperationType.AI_GENERATION,
                            post_slug=post.slug
                        )

                        logger.error("Post processing failed",
                                   post_slug=post.slug,
                                   error=e)

                        # Try to create an error report for debugging
                        try:
                            error_report = {
                                "post_slug": post.slug,
                                "post_title": post.title,
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "timestamp": datetime.now().isoformat(),
                                "session_id": metrics.session_id
                            }
                            error_path = Path(config.generated_directory) / f"{post.slug}-error.json"
                            with open(error_path, 'w') as f:
                                json.dump(error_report, f, indent=2)
                            logger.info("Error report saved",
                                       post_slug=post.slug,
                                       error_path=str(error_path))
                        except Exception as report_error:
                            logger.warning("Failed to save error report",
                                         post_slug=post.slug,
                                         error=report_error)

                        continue

            # Generate comprehensive metrics report
            metrics_report = metrics.get_comprehensive_report()

            # Log final statistics
            logger.info("WORKFLOW COMPLETION SUMMARY")
            logger.info("Posts processed", count=posts_processed)
            logger.info("Threads generated", count=threads_generated)

            success_rate = (threads_generated/posts_processed*100) if posts_processed > 0 else 0
            logger.info("Generation success rate", rate_percent=f"{success_rate:.1f}%")

            # Display API and performance statistics
            api_stats = metrics_report.get('api_statistics', {})
            if api_stats:
                logger.info("API call statistics",
                           total_calls=api_stats.get('total_calls', 0),
                           success_rate=f"{api_stats.get('success_rate', 0):.1f}%",
                           avg_response_time=f"{api_stats.get('average_response_time_ms', 0):.1f}ms",
                           total_tokens=api_stats.get('total_tokens_used', 0))

            # Display auto-posting statistics
            try:
                posting_stats = output_manager.get_posting_statistics()
                logger.info("Auto-posting statistics",
                           successful_posts=posting_stats['successful_posts'],
                           failed_posts=posting_stats['failed_posts'],
                           pr_created=pr_created)
            except Exception as e:
                logger.warning("Could not retrieve posting statistics", error=e)

            # Display error statistics
            error_stats = metrics_report.get('error_statistics', {})
            if error_stats.get('total_errors', 0) > 0:
                logger.info("Error statistics",
                           total_errors=error_stats.get('total_errors', 0),
                           error_categories=error_stats.get('category_breakdown', {}))

            # Save metrics report
            try:
                metrics_report_path = Path(config.generated_directory) / f"metrics-{metrics.session_id}.json"
                metrics.save_metrics_report(str(metrics_report_path))
                logger.info("Metrics report saved", report_path=str(metrics_report_path))
            except Exception as e:
                logger.warning("Failed to save metrics report", error=e)

            # Generate and save monitoring dashboard report
            try:
                dashboard_report_path = Path(config.generated_directory) / f"dashboard-{metrics.session_id}.json"
                dashboard.save_dashboard_report(str(dashboard_report_path))
                logger.info("Dashboard report saved", report_path=str(dashboard_report_path))
            except Exception as e:
                logger.warning("Failed to save dashboard report", error=e)

            # Perform final health check and display summary
            try:
                system_health = health_monitor.perform_health_checks()
                logger.info("Final system health check",
                           overall_status=system_health.overall_status.value,
                           checks_passed=len([c for c in system_health.checks if c.status.value == "healthy"]),
                           total_checks=len(system_health.checks),
                           active_alerts=len(health_monitor.get_active_alerts()))

                # Print monitoring summary to console for GitHub Actions logs
                dashboard.print_summary_report()

            except Exception as e:
                logger.warning("Failed to perform final health check", error=e)

        except Exception as e:
            metrics.record_error(
                error_category=metrics.ErrorCategory.UNKNOWN_ERROR,
                error=e,
                operation_type=OperationType.CONTENT_DETECTION
            )
            logger.error("Workflow execution failed", error=e)
            return 1

        finally:
            # Set final GitHub Actions outputs
            set_github_actions_outputs(threads_generated, posts_processed, pr_created)

            # Set additional metrics outputs for GitHub Actions
            metrics.set_github_actions_outputs()

        logger.info("Tweet thread generator completed successfully",
                   session_id=metrics.session_id,
                   total_operations=len(metrics.operation_metrics))
        return 0

    except KeyboardInterrupt:
        logger.info("Tweet thread generator interrupted by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        if 'metrics' in locals():
            metrics.record_error(
                error_category=metrics.ErrorCategory.UNKNOWN_ERROR,
                error=e
            )
        logger.error("Fatal error in tweet generator", error=e)
        return 1


if __name__ == "__main__":
    sys.exit(main())