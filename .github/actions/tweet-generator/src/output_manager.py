"""
Output management and GitHub integration for the Tweet Thread Generator.

This module handles file operations, PR creation, auto-posting functionality,
and GitHub API integration for the tweet generation workflow.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from github import Github

from models import ThreadData, BlogPost, PostResult, GeneratorConfig
from exceptions import GitHubAPIError, TwitterAPIError, FileOperationError
from utils import save_json_file, ensure_directory, get_repository_info, sanitize_slug_for_filename
from twitter_client import TwitterClient
from auto_poster import AutoPoster
from logger import get_logger, OperationType
from metrics import get_metrics_collector, ErrorCategory


class OutputManager:
    """Manages output operations and external integrations."""

    def __init__(self, config: GeneratorConfig):
        """
        Initialize output manager.

        Args:
            config: GeneratorConfig with all settings
        """
        self.config = config
        self.github_token = config.github_token
        self.generated_dir = Path(config.generated_directory)
        self.posted_dir = Path(config.posted_directory)
        self.github_client = None
        self.auto_poster = AutoPoster(config)
        self.logger = get_logger()
        self.metrics = get_metrics_collector()

        if self.github_token:
            self.github_client = Github(self.github_token)

    def save_thread_draft(self, thread: ThreadData, output_path: Optional[str] = None) -> str:
        """
        Save tweet thread draft to JSON file.

        Args:
            thread: ThreadData to save
            output_path: Optional custom output path

        Returns:
            Path to saved file

        Raises:
            FileOperationError: If saving fails
        """
        try:
            # Ensure generated directory exists
            ensure_directory(self.generated_dir)

            # Determine output path
            if output_path is None:
                # Sanitize slug for filename
                sanitized_slug = sanitize_slug_for_filename(thread.post_slug)
                filename = f"{sanitized_slug}-thread.json"
                output_path = self.generated_dir / filename
            else:
                output_path = Path(output_path)

            # Create backup if file already exists
            if output_path.exists():
                self._backup_existing_file(output_path)

            # Convert thread to dictionary with metadata
            thread_data = thread.to_dict()

            # Add generation metadata
            thread_data["metadata"] = {
                "generated_at": thread.generated_at.isoformat(),
                "model_used": thread.model_used,
                "prompt_version": thread.prompt_version,
                "style_profile_version": thread.style_profile_version,
                "generator_version": "1.0.0",
                "file_version": 1
            }

            # Save to JSON file
            success = save_json_file(thread_data, output_path, indent=2)
            if not success:
                raise FileOperationError(f"Failed to save thread draft to {output_path}")

            return str(output_path)

        except Exception as e:
            raise FileOperationError(f"Error saving thread draft: {str(e)}")

    def _backup_existing_file(self, file_path: Path) -> None:
        """
        Create backup of existing file with timestamp.

        Args:
            file_path: Path to file to backup
        """
        if not file_path.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = file_path.parent / backup_name

        try:
            import shutil
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            # Log warning but don't fail the operation
            print(f"Warning: Failed to create backup of {file_path}: {e}")

    def generate_thread_preview(self, thread: ThreadData, post: BlogPost) -> str:
        """
        Generate a formatted preview of the thread for PR descriptions.

        Args:
            thread: ThreadData to preview
            post: Source BlogPost

        Returns:
            Formatted thread preview text
        """
        preview_lines = []

        # Header
        preview_lines.append(f"# Tweet Thread Preview: {post.title}")
        preview_lines.append("")
        preview_lines.append(f"**Source Post:** {post.canonical_url}")
        preview_lines.append(f"**Categories:** {', '.join(post.categories)}")
        preview_lines.append(f"**Generated:** {thread.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        preview_lines.append(f"**Model Used:** {thread.model_used}")
        preview_lines.append(f"**Engagement Score:** {thread.engagement_score:.2f}")
        preview_lines.append("")

        # Hook variations
        if thread.hook_variations:
            preview_lines.append("## Hook Variations")
            for i, hook in enumerate(thread.hook_variations, 1):
                preview_lines.append(f"{i}. {hook}")
            preview_lines.append("")

        # Thread content
        preview_lines.append("## Thread Content")
        preview_lines.append("")

        for i, tweet in enumerate(thread.tweets, 1):
            # Tweet header with character count
            char_count = tweet.character_count
            char_indicator = "✅" if char_count <= 280 else "⚠️"
            preview_lines.append(f"### Tweet {i}/{ len(thread.tweets)} {char_indicator} ({char_count}/280 chars)")

            # Tweet content
            preview_lines.append("```")
            preview_lines.append(tweet.content)
            preview_lines.append("```")

            # Engagement elements if present
            if tweet.engagement_elements:
                preview_lines.append(f"*Engagement elements: {', '.join(tweet.engagement_elements)}*")

            preview_lines.append("")

        # Hashtags
        if thread.hashtags:
            preview_lines.append("## Suggested Hashtags")
            hashtag_text = " ".join([f"#{tag}" for tag in thread.hashtags])
            preview_lines.append(hashtag_text)
            preview_lines.append("")

        # Thread plan if available
        if thread.thread_plan:
            preview_lines.append("## Thread Strategy")
            preview_lines.append(f"**Hook Type:** {thread.thread_plan.hook_type.value}")
            preview_lines.append(f"**Engagement Strategy:** {thread.thread_plan.engagement_strategy}")
            if thread.thread_plan.call_to_action:
                preview_lines.append(f"**Call to Action:** {thread.thread_plan.call_to_action}")
            preview_lines.append("")

        # Review instructions
        preview_lines.append("## Review Instructions")
        preview_lines.append("- ✅ Check that the thread accurately represents the blog post content")
        preview_lines.append("- ✅ Verify that the tone matches your writing style")
        preview_lines.append("- ✅ Ensure all tweets are under 280 characters")
        preview_lines.append("- ✅ Review engagement elements and hashtags for appropriateness")
        preview_lines.append("- ✅ Approve this PR to save the thread draft, or request changes")

        if post.auto_post:
            preview_lines.append("- ⚠️ **Auto-posting is enabled** - this thread will be posted automatically when merged")

        return "\n".join(preview_lines)

    def create_or_update_pr(self, thread: ThreadData, post: BlogPost) -> str:
        """
        Create or update pull request for thread review.

        Args:
            thread: ThreadData with generated content
            post: Source BlogPost

        Returns:
            PR URL

        Raises:
            GitHubAPIError: If PR operations fail
        """
        try:
            if not self.github_client:
                raise GitHubAPIError("GitHub client not initialized")

            # Get repository information
            repo_info = get_repository_info()
            repo_name = repo_info.get("repository")
            if not repo_name:
                raise GitHubAPIError("Repository information not available")

            repo = self.github_client.get_repo(repo_name)

            # Generate branch name for the PR (sanitize for Git ref naming)
            sanitized_slug = sanitize_slug_for_filename(post.slug)
            branch_name = f"tweet-thread/{sanitized_slug}"
            pr_title = f"Tweet thread for: {post.title}"

            # Check if PR already exists
            existing_pr = self._find_existing_pr(repo, branch_name, pr_title)

            if existing_pr:
                # Update existing PR
                pr_body = self._create_pr_body(thread, post)
                existing_pr.edit(title=pr_title, body=pr_body)

                # Add comment about update
                update_comment = f"🔄 Thread updated at {thread.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                existing_pr.create_issue_comment(update_comment)

                return existing_pr.html_url
            else:
                # Create new PR
                return self._create_new_pr(repo, thread, post, branch_name, pr_title, sanitized_slug)

        except Exception as e:
            raise GitHubAPIError(f"Failed to create or update PR: {str(e)}")

    def _find_existing_pr(self, repo, branch_name: str, pr_title: str):
        """
        Find existing PR for the thread.

        Args:
            repo: GitHub repository object
            branch_name: Branch name to search for
            pr_title: PR title to match

        Returns:
            Existing PR object or None
        """
        try:
            # Search for open PRs with matching title
            pulls = repo.get_pulls(state='open')
            for pr in pulls:
                if pr.title == pr_title or branch_name in pr.head.ref:
                    return pr
            return None
        except Exception:
            return None

    def _create_new_pr(self, repo, thread: ThreadData, post: BlogPost, branch_name: str, pr_title: str, sanitized_slug: str) -> str:
        """
        Create a new pull request.

        Args:
            repo: GitHub repository object
            thread: ThreadData with generated content
            post: Source BlogPost
            branch_name: Branch name for PR
            pr_title: PR title

        Returns:
            PR URL
        """
        try:
            # Get default branch
            default_branch = repo.default_branch

            # Create new branch from default branch
            source_branch = repo.get_branch(default_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source_branch.commit.sha)

            # Save thread draft file to the new branch (use sanitized slug for filename)
            thread_file_path = f"{self.generated_dir}/{sanitized_slug}-thread.json"
            thread_content = json.dumps(thread.to_dict(), indent=2, default=str)

            # Create or update file in the branch
            try:
                # Try to get existing file
                existing_file = repo.get_contents(thread_file_path, ref=branch_name)
                repo.update_file(
                    path=thread_file_path,
                    message=f"Update tweet thread for {post.title}",
                    content=thread_content,
                    sha=existing_file.sha,
                    branch=branch_name
                )
            except:
                # File doesn't exist, create new one
                repo.create_file(
                    path=thread_file_path,
                    message=f"Add tweet thread for {post.title}",
                    content=thread_content,
                    branch=branch_name
                )

            # Create PR body
            pr_body = self._create_pr_body(thread, post)

            # Create pull request
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=default_branch
            )

            # Assign PR to repository owner
            try:
                owner = repo.owner.login
                pr.add_to_assignees(owner)
            except Exception as e:
                print(f"Warning: Could not assign PR to owner: {e}")

            # Add labels
            try:
                labels = ["tweet-thread", "content", "review-needed"]
                pr.add_to_labels(*labels)
            except Exception as e:
                print(f"Warning: Could not add labels to PR: {e}")

            return pr.html_url

        except Exception as e:
            raise GitHubAPIError(f"Failed to create new PR: {str(e)}")

    def post_to_twitter(self, thread: ThreadData, post: BlogPost) -> PostResult:
        """
        Post thread to Twitter/X platform using auto-posting logic.

        Args:
            thread: ThreadData to post
            post: BlogPost being posted (for auto-posting checks)

        Returns:
            PostResult with posting status

        Raises:
            TwitterAPIError: If posting fails
        """
        return self.auto_poster.attempt_auto_post(thread, post)

    def save_posted_metadata(self, post_slug: str, result: PostResult) -> None:
        """
        Save posted metadata to tracking file.

        Args:
            post_slug: Slug of the posted post
            result: PostResult with posting information

        Raises:
            FileOperationError: If saving fails
        """
        self.auto_poster.save_posted_metadata(post_slug, result)

    def check_already_posted(self, post_slug: str) -> bool:
        """
        Check if post has already been posted to social media.

        Args:
            post_slug: Post slug to check

        Returns:
            True if already posted, False otherwise
        """
        return self.auto_poster.is_already_posted(post_slug)

    def _create_pr_body(self, thread: ThreadData, post: BlogPost) -> str:
        """
        Create PR body with thread preview and metadata.

        Args:
            thread: ThreadData with generated content
            post: Source BlogPost

        Returns:
            Formatted PR body text
        """
        # Generate thread preview
        preview = self.generate_thread_preview(thread, post)

        # Add PR-specific content
        pr_body_lines = [
            "## 🧵 Generated Tweet Thread",
            "",
            "This PR contains an AI-generated tweet thread based on your latest blog post.",
            "",
            preview,
            "",
            "---",
            "",
            "## 📋 Next Steps",
            "",
            "1. **Review the thread content** above for accuracy and tone",
            "2. **Check character limits** - tweets over 280 chars are marked with ⚠️",
            "3. **Verify engagement elements** match your style preferences",
            "4. **Approve and merge** this PR to save the thread draft",
        ]

        if post.auto_post:
            pr_body_lines.extend([
                "5. **⚠️ Auto-posting enabled** - thread will be posted to Twitter automatically",
                "",
                "> **Note:** This post has `auto_post: true` in its frontmatter. The thread will be posted to Twitter/X automatically when this PR is merged."
            ])
        else:
            pr_body_lines.extend([
                "5. **Manual posting** - use the saved draft to post manually",
                "",
                "> **Note:** Auto-posting is disabled. You can use the generated thread draft for manual posting."
            ])

        pr_body_lines.extend([
            "",
            "---",
            "",
            "## 🤖 Generation Details",
            "",
            f"- **Model:** {thread.model_used}",
            f"- **Prompt Version:** {thread.prompt_version}",
            f"- **Style Profile Version:** {thread.style_profile_version}",
            f"- **Generated At:** {thread.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"- **Engagement Score:** {thread.engagement_score:.2f}/10",
            "",
            "*This thread was generated automatically by the Tweet Thread Generator action.*"
        ])

        return "\n".join(pr_body_lines)

    def _setup_github_client(self) -> None:
        """Set up GitHub API client with authentication and error handling."""
        try:
            if not self.github_token:
                raise GitHubAPIError("GitHub token not provided")

            # Initialize GitHub client with token
            self.github_client = Github(self.github_token)

            # Test authentication by getting user info
            user = self.github_client.get_user()
            print(f"GitHub API authenticated as: {user.login}")

        except Exception as e:
            raise GitHubAPIError(f"Failed to setup GitHub client: {str(e)}")

    def get_repository_metadata(self) -> Dict[str, Any]:
        """
        Extract repository metadata from GitHub API and environment.

        Returns:
            Dictionary with repository information

        Raises:
            GitHubAPIError: If repository access fails
        """
        try:
            if not self.github_client:
                self._setup_github_client()

            # Get repository info from environment
            repo_info = get_repository_info()
            repo_name = repo_info.get("repository")

            if not repo_name:
                raise GitHubAPIError("Repository name not available in environment")

            # Get repository object from GitHub API
            repo = self.github_client.get_repo(repo_name)

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "owner": repo.owner.login,
                "default_branch": repo.default_branch,
                "private": repo.private,
                "description": repo.description,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "language": repo.language,
                "topics": repo.get_topics(),
                "environment_info": repo_info
            }

        except Exception as e:
            raise GitHubAPIError(f"Failed to get repository metadata: {str(e)}")

    def create_or_update_file(self, file_path: str, content: str, commit_message: str,
                             branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Create or update a file in the repository.

        Args:
            file_path: Path to file in repository
            content: File content
            commit_message: Commit message
            branch: Branch name (defaults to default branch)

        Returns:
            Dictionary with commit information

        Raises:
            GitHubAPIError: If file operations fail
        """
        try:
            if not self.github_client:
                self._setup_github_client()

            repo_info = get_repository_info()
            repo_name = repo_info.get("repository")
            repo = self.github_client.get_repo(repo_name)

            if branch is None:
                branch = repo.default_branch

            try:
                # Try to get existing file
                existing_file = repo.get_contents(file_path, ref=branch)

                # Update existing file
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )

                return {
                    "action": "updated",
                    "path": file_path,
                    "sha": result["commit"].sha,
                    "commit_url": result["commit"].html_url,
                    "branch": branch
                }

            except Exception:
                # File doesn't exist, create new one
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )

                return {
                    "action": "created",
                    "path": file_path,
                    "sha": result["commit"].sha,
                    "commit_url": result["commit"].html_url,
                    "branch": branch
                }

        except Exception as e:
            raise GitHubAPIError(f"Failed to create or update file {file_path}: {str(e)}")

    def handle_rate_limiting(self, operation_name: str) -> None:
        """
        Handle GitHub API rate limiting.

        Args:
            operation_name: Name of operation for logging

        Raises:
            GitHubAPIError: If rate limit handling fails
        """
        try:
            if not self.github_client:
                return

            # Get rate limit info
            rate_limit = self.github_client.get_rate_limit()
            core_limit = rate_limit.core

            print(f"GitHub API Rate Limit Status for {operation_name}:")
            print(f"  Remaining: {core_limit.remaining}/{core_limit.limit}")
            print(f"  Reset time: {core_limit.reset}")

            # Check if we're close to rate limit
            if core_limit.remaining < 10:
                import time
                reset_time = core_limit.reset.timestamp()
                current_time = time.time()
                sleep_time = max(0, reset_time - current_time + 60)  # Add 1 minute buffer

                if sleep_time > 0:
                    print(f"Rate limit nearly exceeded. Waiting {sleep_time:.0f} seconds...")
                    time.sleep(sleep_time)

        except Exception as e:
            print(f"Warning: Could not check rate limit for {operation_name}: {e}")

    def validate_github_permissions(self) -> Dict[str, bool]:
        """
        Validate GitHub token permissions for required operations.

        Returns:
            Dictionary with permission validation results
        """
        permissions = {
            "read_repository": False,
            "write_repository": False,
            "create_pull_requests": False,
            "read_user": False
        }

        try:
            if not self.github_client:
                self._setup_github_client()

            # Test user access
            try:
                user = self.github_client.get_user()
                permissions["read_user"] = True
            except Exception:
                pass

            # Test repository access
            repo_info = get_repository_info()
            repo_name = repo_info.get("repository")

            if repo_name:
                try:
                    repo = self.github_client.get_repo(repo_name)
                    permissions["read_repository"] = True

                    # Test write permissions by checking if we can create a branch
                    # (This is a read-only test, we don't actually create anything)
                    if repo.permissions.push:
                        permissions["write_repository"] = True
                        permissions["create_pull_requests"] = True

                except Exception:
                    pass

        except Exception as e:
            print(f"Warning: Could not validate GitHub permissions: {e}")

        return permissions

    def _commit_and_push_files(self, files: Dict[str, str], commit_message: str,
                              branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Commit and push multiple files to repository.

        Args:
            files: Dictionary of file paths to content
            commit_message: Commit message
            branch: Branch name (defaults to default branch)

        Returns:
            Dictionary with commit information

        Raises:
            GitHubAPIError: If git operations fail
        """
        try:
            if not self.github_client:
                self._setup_github_client()

            if not files:
                raise GitHubAPIError("No files provided for commit")

            repo_info = get_repository_info()
            repo_name = repo_info.get("repository")
            repo = self.github_client.get_repo(repo_name)

            if branch is None:
                branch = repo.default_branch

            # Check rate limiting before operations
            self.handle_rate_limiting("commit_and_push_files")

            # Get the current commit SHA for the branch
            branch_ref = repo.get_git_ref(f"heads/{branch}")
            base_commit = repo.get_git_commit(branch_ref.object.sha)

            # Create blobs for each file
            blobs = {}
            for file_path, content in files.items():
                blob = repo.create_git_blob(content, "utf-8")
                blobs[file_path] = blob.sha

            # Get the base tree
            base_tree = base_commit.tree

            # Create tree elements for new/updated files
            tree_elements = []
            for file_path, blob_sha in blobs.items():
                tree_elements.append({
                    "path": file_path,
                    "mode": "100644",  # Regular file mode
                    "type": "blob",
                    "sha": blob_sha
                })

            # Create new tree
            new_tree = repo.create_git_tree(tree_elements, base_tree)

            # Create commit
            commit = repo.create_git_commit(
                message=commit_message,
                tree=new_tree,
                parents=[base_commit]
            )

            # Update branch reference
            branch_ref.edit(commit.sha)

            return {
                "commit_sha": commit.sha,
                "commit_url": commit.html_url,
                "branch": branch,
                "files_committed": list(files.keys()),
                "commit_message": commit_message
            }

        except Exception as e:
            raise GitHubAPIError(f"Failed to commit and push files: {str(e)}")

    def batch_file_operations(self, operations: List[Dict[str, Any]],
                             commit_message: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform multiple file operations in a single commit.

        Args:
            operations: List of file operations with 'action', 'path', and 'content'
            commit_message: Commit message
            branch: Branch name (defaults to default branch)

        Returns:
            Dictionary with operation results

        Raises:
            GitHubAPIError: If batch operations fail
        """
        try:
            # Validate operations
            valid_actions = ['create', 'update', 'delete']
            files_to_commit = {}

            for op in operations:
                action = op.get('action')
                path = op.get('path')
                content = op.get('content', '')

                if action not in valid_actions:
                    raise GitHubAPIError(f"Invalid action '{action}'. Must be one of: {valid_actions}")

                if not path:
                    raise GitHubAPIError("File path is required for all operations")

                if action in ['create', 'update']:
                    files_to_commit[path] = content
                # Note: Delete operations would need special handling in the tree creation

            # Commit all files at once
            if files_to_commit:
                return self._commit_and_push_files(files_to_commit, commit_message, branch)
            else:
                return {"message": "No files to commit"}

        except Exception as e:
            raise GitHubAPIError(f"Failed to perform batch file operations: {str(e)}")

    def should_auto_post(self, post: BlogPost) -> tuple[bool, str]:
        """
        Check if a post should be auto-posted.

        Args:
            post: BlogPost to check

        Returns:
            Tuple of (should_post, reason)
        """
        return self.auto_poster.should_auto_post(post)

    def get_posted_metadata(self, post_slug: str) -> Optional[Dict[str, Any]]:
        """
        Get posted metadata for a post.

        Args:
            post_slug: Slug of the post

        Returns:
            Posted metadata dict, or None if not found
        """
        return self.auto_poster.get_posted_metadata(post_slug)

    def get_posting_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about posted threads.

        Returns:
            Dictionary with posting statistics
        """
        return self.auto_poster.get_posting_statistics()

    def validate_auto_posting_setup(self) -> List[str]:
        """
        Validate auto-posting setup and return any issues.

        Returns:
            List of validation issues (empty if setup is valid)
        """
        return self.auto_poster.validate_auto_posting_setup()

    def list_posted_threads(self) -> List[Dict[str, Any]]:
        """
        List all posted threads with metadata.

        Returns:
            List of posted thread metadata
        """
        return self.auto_poster.list_posted_threads()

    def cleanup_failed_posts(self, post_slug: str, tweet_ids: List[str]) -> None:
        """
        Clean up partially posted threads by deleting tweets.

        Args:
            post_slug: Slug of the post
            tweet_ids: List of tweet IDs to delete
        """
        self.auto_poster.cleanup_failed_posts(post_slug, tweet_ids)