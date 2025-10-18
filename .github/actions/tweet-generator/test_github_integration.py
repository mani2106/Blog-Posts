"""
GitHub integration tests for the Tweet Thread Generator.

This module tests GitHub API integration including PR creation, file operations,
and error handling as specified in requirements 3.2, 3.3, and 3.4.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from output_manager import OutputManager
from models import (
    BlogPost, ThreadData, Tweet, GeneratorConfig,
    PostResult, HookType, ThreadPlan, EngagementLevel
)
from exceptions import GitHubAPIError, FileOperationError
from utils import get_repository_info


class TestGitHubIntegration:
    """Test suite for GitHub API integration functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generated_dir = self.temp_dir / ".generated"
        self.posted_dir = self.temp_dir / ".posted"

        # Create directories
        self.generated_dir.mkdir(parents=True)
        self.posted_dir.mkdir(parents=True)

        # Create test configuration
        self.config = GeneratorConfig(
            github_token="test_token",
            generated_directory=str(self.generated_dir),
            posted_directory=str(self.posted_dir),
            engagement_optimization_level=EngagementLevel.HIGH
        )

        # Create sample blog post
        self.sample_post = BlogPost(
            file_path="_posts/2024-01-01-test-post.md",
            title="Test Blog Post",
            content="This is a test blog post content.",
            frontmatter={
                "title": "Test Blog Post",
                "date": "2024-01-01",
                "categories": ["test", "blog"],
                "publish": True
            },
            canonical_url="https://example.com/test-post",
            categories=["test", "blog"],
            summary="A test blog post",
            auto_post=False,
            slug="test-post"
        )

        # Create sample thread data
        self.sample_tweets = [
            Tweet(
                content="🧵 Thread about test blog post (1/3)",
                character_count=45,
                engagement_elements=["emoji", "thread_indicator"],
                hashtags=[],
                position=1
            ),
            Tweet(
                content="Here's the main content of the post with some insights. #testing",
                character_count=68,
                engagement_elements=["hashtag"],
                hashtags=["testing"],
                position=2
            ),
            Tweet(
                content="Read the full post here: https://example.com/test-post",
                character_count=55,
                engagement_elements=["url"],
                hashtags=[],
                position=3
            )
        ]

        self.sample_thread = ThreadData(
            post_slug="test-post",
            tweets=self.sample_tweets,
            hook_variations=["Hook 1", "Hook 2", "Hook 3"],
            hashtags=["testing", "blog"],
            engagement_score=8.5,
            model_used="google/gemini-2.5-flash-lite",
            prompt_version="1.0",
            generated_at=datetime.now(),
            style_profile_version="1.0",
            thread_plan=ThreadPlan(
                hook_type=HookType.CURIOSITY,
                estimated_tweets=3,
                engagement_strategy="informative",
                call_to_action="Read the full post"
            )
        )

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_github_client_initialization(self, mock_repo_info, mock_github):
        """Test GitHub client initialization with proper authentication."""
        # Setup mocks
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github_instance = Mock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        # Initialize output manager
        output_manager = OutputManager(self.config)

        # Verify GitHub client was initialized with token
        mock_github.assert_called_once_with("test_token")
        assert output_manager.github_client is not None

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_create_new_pr_success(self, mock_repo_info, mock_github):
        """Test successful creation of new pull request."""
        # Setup repository info mock
        mock_repo_info.return_value = {
            "repository": "testuser/test-repo",
            "ref": "refs/heads/main",
            "sha": "abc123"
        }

        # Setup GitHub API mocks
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_repo.owner.login = "testuser"

        # Mock branch operations
        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref = Mock()

        # Mock file operations - simulate file doesn't exist initially
        mock_repo.get_contents.side_effect = Exception("File not found")
        mock_repo.create_file = Mock()

        # Mock PR creation
        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/testuser/test-repo/pull/1"
        mock_repo.create_pull.return_value = mock_pr
        mock_repo.get_pulls.return_value = []  # No existing PRs

        # Mock PR assignment and labeling
        mock_pr.add_to_assignees = Mock()
        mock_pr.add_to_labels = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Create output manager and test PR creation
        output_manager = OutputManager(self.config)
        pr_url = output_manager.create_or_update_pr(self.sample_thread, self.sample_post)

        # Verify PR creation workflow
        assert pr_url == "https://github.com/testuser/test-repo/pull/1"
        mock_repo.create_git_ref.assert_called_once()
        mock_repo.create_file.assert_called_once()
        mock_repo.create_pull.assert_called_once()
        mock_pr.add_to_assignees.assert_called_once_with("testuser")
        mock_pr.add_to_labels.assert_called_once()

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_update_existing_pr(self, mock_repo_info, mock_github):
        """Test updating an existing pull request."""
        # Setup repository info mock
        mock_repo_info.return_value = {
            "repository": "testuser/test-repo"
        }

        # Setup existing PR mock
        mock_existing_pr = Mock()
        mock_existing_pr.title = "Tweet thread for: Test Blog Post"
        mock_existing_pr.html_url = "https://github.com/testuser/test-repo/pull/1"
        mock_existing_pr.head.ref = "tweet-thread/test-post"
        mock_existing_pr.edit = Mock()
        mock_existing_pr.create_issue_comment = Mock()

        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_existing_pr]

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Create output manager and test PR update
        output_manager = OutputManager(self.config)
        pr_url = output_manager.create_or_update_pr(self.sample_thread, self.sample_post)

        # Verify PR update workflow
        assert pr_url == "https://github.com/testuser/test-repo/pull/1"
        mock_existing_pr.edit.assert_called_once()
        mock_existing_pr.create_issue_comment.assert_called_once()

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_pr_creation_with_auto_post_flag(self, mock_repo_info, mock_github):
        """Test PR creation includes auto-post warning when enabled."""
        # Setup auto-post enabled post
        auto_post_post = BlogPost(
            file_path="_posts/2024-01-01-auto-post.md",
            title="Auto Post Test",
            content="This post will be auto-posted.",
            frontmatter={"auto_post": True},
            canonical_url="https://example.com/auto-post",
            auto_post=True,
            slug="auto-post"
        )

        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.get_pulls.return_value = []
        mock_repo.default_branch = "main"
        mock_repo.owner.login = "testuser"

        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref = Mock()
        mock_repo.create_file = Mock()

        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/testuser/test-repo/pull/1"
        mock_repo.create_pull.return_value = mock_pr
        mock_pr.add_to_assignees = Mock()
        mock_pr.add_to_labels = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Create output manager and test PR creation
        output_manager = OutputManager(self.config)
        pr_url = output_manager.create_or_update_pr(self.sample_thread, auto_post_post)

        # Verify PR was created and body contains auto-post warning
        mock_repo.create_pull.assert_called_once()
        call_args = mock_repo.create_pull.call_args
        pr_body = call_args[1]['body']
        assert "⚠️ Auto-posting enabled" in pr_body
        assert "auto_post: true" in pr_body

    def test_generate_thread_preview(self):
        """Test thread preview generation for PR descriptions."""
        output_manager = OutputManager(self.config)
        preview = output_manager.generate_thread_preview(self.sample_thread, self.sample_post)

        # Verify preview contains expected sections
        assert "# Tweet Thread Preview: Test Blog Post" in preview
        assert "**Source Post:** https://example.com/test-post" in preview
        assert "**Categories:** test, blog" in preview
        assert "**Model Used:** google/gemini-2.5-flash-lite" in preview
        assert "**Engagement Score:** 8.50" in preview

        # Verify hook variations section
        assert "## Hook Variations" in preview
        assert "1. Hook 1" in preview
        assert "2. Hook 2" in preview
        assert "3. Hook 3" in preview

        # Verify thread content section
        assert "## Thread Content" in preview
        assert "### Tweet 1/3" in preview
        assert "### Tweet 2/3" in preview
        assert "### Tweet 3/3" in preview

        # Verify character count indicators
        assert "(45/280 chars)" in preview
        assert "(68/280 chars)" in preview
        assert "(55/280 chars)" in preview

        # Verify hashtags section
        assert "## Suggested Hashtags" in preview
        assert "#testing #blog" in preview

        # Verify review instructions
        assert "## Review Instructions" in preview
        assert "✅ Check that the thread accurately represents" in preview

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_create_or_update_file_new_file(self, mock_repo_info, mock_github):
        """Test creating a new file in the repository."""
        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_repo.get_contents.side_effect = Exception("File not found")  # Simulate file doesn't exist

        mock_commit_result = {
            "commit": Mock(sha="def456", html_url="https://github.com/testuser/test-repo/commit/def456")
        }
        mock_repo.create_file.return_value = mock_commit_result

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test file creation
        output_manager = OutputManager(self.config)
        result = output_manager.create_or_update_file(
            "test-file.json",
            '{"test": "content"}',
            "Add test file"
        )

        # Verify file creation
        mock_repo.create_file.assert_called_once_with(
            path="test-file.json",
            message="Add test file",
            content='{"test": "content"}',
            branch="main"
        )

        assert result["action"] == "created"
        assert result["path"] == "test-file.json"
        assert result["sha"] == "def456"
        assert result["branch"] == "main"

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_create_or_update_file_existing_file(self, mock_repo_info, mock_github):
        """Test updating an existing file in the repository."""
        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.default_branch = "main"

        # Mock existing file
        mock_existing_file = Mock()
        mock_existing_file.sha = "abc123"
        mock_repo.get_contents.return_value = mock_existing_file

        mock_commit_result = {
            "commit": Mock(sha="def456", html_url="https://github.com/testuser/test-repo/commit/def456")
        }
        mock_repo.update_file.return_value = mock_commit_result

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test file update
        output_manager = OutputManager(self.config)
        result = output_manager.create_or_update_file(
            "existing-file.json",
            '{"updated": "content"}',
            "Update existing file"
        )

        # Verify file update
        mock_repo.update_file.assert_called_once_with(
            path="existing-file.json",
            message="Update existing file",
            content='{"updated": "content"}',
            sha="abc123",
            branch="main"
        )

        assert result["action"] == "updated"
        assert result["path"] == "existing-file.json"
        assert result["sha"] == "def456"
        assert result["branch"] == "main"

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_batch_file_operations(self, mock_repo_info, mock_github):
        """Test batch file operations with multiple files in single commit."""
        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.default_branch = "main"

        # Mock git operations
        mock_branch_ref = Mock()
        mock_branch_ref.object.sha = "base123"
        mock_repo.get_git_ref.return_value = mock_branch_ref

        mock_base_commit = Mock()
        mock_base_commit.tree = Mock()
        mock_repo.get_git_commit.return_value = mock_base_commit

        # Mock blob creation
        mock_blob1 = Mock(sha="blob1")
        mock_blob2 = Mock(sha="blob2")
        mock_repo.create_git_blob.side_effect = [mock_blob1, mock_blob2]

        # Mock tree and commit creation
        mock_new_tree = Mock()
        mock_repo.create_git_tree.return_value = mock_new_tree

        mock_commit = Mock()
        mock_commit.sha = "commit123"
        mock_commit.html_url = "https://github.com/testuser/test-repo/commit/commit123"
        mock_repo.create_git_commit.return_value = mock_commit

        mock_branch_ref.edit = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test batch operations
        output_manager = OutputManager(self.config)
        operations = [
            {"action": "create", "path": "file1.json", "content": '{"file": 1}'},
            {"action": "update", "path": "file2.json", "content": '{"file": 2}'}
        ]

        result = output_manager.batch_file_operations(
            operations,
            "Batch update multiple files"
        )

        # Verify batch operations
        assert mock_repo.create_git_blob.call_count == 2
        mock_repo.create_git_tree.assert_called_once()
        mock_repo.create_git_commit.assert_called_once()
        mock_branch_ref.edit.assert_called_once_with("commit123")

        assert result["commit_sha"] == "commit123"
        assert result["files_committed"] == ["file1.json", "file2.json"]
        assert result["commit_message"] == "Batch update multiple files"

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_get_repository_metadata(self, mock_repo_info, mock_github):
        """Test repository metadata extraction."""
        # Setup repository info mock
        mock_repo_info.return_value = {
            "repository": "testuser/test-repo",
            "ref": "refs/heads/main",
            "sha": "abc123"
        }

        # Setup GitHub repo mock
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "testuser/test-repo"
        mock_repo.owner.login = "testuser"
        mock_repo.default_branch = "main"
        mock_repo.private = False
        mock_repo.description = "Test repository"
        mock_repo.html_url = "https://github.com/testuser/test-repo"
        mock_repo.clone_url = "https://github.com/testuser/test-repo.git"
        mock_repo.ssh_url = "git@github.com:testuser/test-repo.git"
        mock_repo.created_at = datetime(2024, 1, 1)
        mock_repo.updated_at = datetime(2024, 1, 15)
        mock_repo.language = "Python"
        mock_repo.get_topics.return_value = ["python", "automation"]

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test metadata extraction
        output_manager = OutputManager(self.config)
        metadata = output_manager.get_repository_metadata()

        # Verify metadata
        assert metadata["name"] == "test-repo"
        assert metadata["full_name"] == "testuser/test-repo"
        assert metadata["owner"] == "testuser"
        assert metadata["default_branch"] == "main"
        assert metadata["private"] is False
        assert metadata["description"] == "Test repository"
        assert metadata["language"] == "Python"
        assert metadata["topics"] == ["python", "automation"]
        assert "environment_info" in metadata

    @patch('output_manager.Github')
    def test_github_api_error_handling(self, mock_github):
        """Test error handling for GitHub API failures."""
        # Setup GitHub client to raise exception
        mock_github.side_effect = Exception("GitHub API Error")

        # Test that exception is raised during initialization
        with pytest.raises(Exception) as exc_info:
            output_manager = OutputManager(self.config)

        assert "GitHub API Error" in str(exc_info.value)

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_pr_creation_api_failure(self, mock_repo_info, mock_github):
        """Test PR creation failure handling."""
        # Setup mocks to fail at repo level
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}

        mock_github_instance = Mock()
        mock_github_instance.get_repo.side_effect = Exception("Repository API Error")
        mock_github.return_value = mock_github_instance

        # Test that GitHubAPIError is raised
        output_manager = OutputManager(self.config)
        with pytest.raises(GitHubAPIError) as exc_info:
            output_manager.create_or_update_pr(self.sample_thread, self.sample_post)

        assert "Failed to create or update PR" in str(exc_info.value)

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_file_operation_api_failure(self, mock_repo_info, mock_github):
        """Test file operation failure handling."""
        # Setup mocks to fail
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.get_contents.side_effect = Exception("API Error")
        mock_repo.create_file.side_effect = Exception("Create failed")

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test that GitHubAPIError is raised
        output_manager = OutputManager(self.config)
        with pytest.raises(GitHubAPIError) as exc_info:
            output_manager.create_or_update_file("test.json", "content", "message")

        assert "Failed to create or update file" in str(exc_info.value)

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    @patch('time.time')
    def test_rate_limiting_handling(self, mock_time, mock_repo_info, mock_github):
        """Test GitHub API rate limiting handling."""
        # Setup rate limit mock
        mock_core_limit = Mock()
        mock_core_limit.remaining = 5  # Low remaining requests
        mock_core_limit.limit = 5000
        mock_core_limit.reset = Mock()
        mock_core_limit.reset.timestamp.return_value = 1640995200  # Future timestamp

        mock_rate_limit = Mock()
        mock_rate_limit.core = mock_core_limit

        mock_github_instance = Mock()
        mock_github_instance.get_rate_limit.return_value = mock_rate_limit
        mock_github.return_value = mock_github_instance

        # Mock current time to be before reset time
        mock_time.return_value = 1640995100  # 100 seconds before reset

        # Test rate limiting check
        output_manager = OutputManager(self.config)

        # This should not raise an exception but should log rate limit info
        with patch('time.sleep') as mock_sleep:
            output_manager.handle_rate_limiting("test_operation")
            # Verify sleep was called due to low remaining requests
            mock_sleep.assert_called_once()

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_validate_github_permissions(self, mock_repo_info, mock_github):
        """Test GitHub token permissions validation."""
        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}

        mock_user = Mock()
        mock_user.login = "testuser"

        mock_repo = Mock()
        mock_repo.permissions.push = True  # Has write permissions

        mock_github_instance = Mock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test permissions validation
        output_manager = OutputManager(self.config)
        permissions = output_manager.validate_github_permissions()

        # Verify permissions
        assert permissions["read_user"] is True
        assert permissions["read_repository"] is True
        assert permissions["write_repository"] is True
        assert permissions["create_pull_requests"] is True

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_validate_github_permissions_limited(self, mock_repo_info, mock_github):
        """Test GitHub permissions validation with limited access."""
        # Setup mocks with limited permissions
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}

        mock_user = Mock()
        mock_user.login = "testuser"

        mock_repo = Mock()
        mock_repo.permissions.push = False  # No write permissions

        mock_github_instance = Mock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test permissions validation
        output_manager = OutputManager(self.config)
        permissions = output_manager.validate_github_permissions()

        # Verify limited permissions
        assert permissions["read_user"] is True
        assert permissions["read_repository"] is True
        assert permissions["write_repository"] is False
        assert permissions["create_pull_requests"] is False

    def test_save_thread_draft_file_operations(self):
        """Test thread draft saving with file operations."""
        output_manager = OutputManager(self.config)

        # Test saving thread draft
        draft_path = output_manager.save_thread_draft(self.sample_thread)

        # Verify file was created
        expected_path = self.generated_dir / "test-post-thread.json"
        assert Path(draft_path) == expected_path
        assert expected_path.exists()

        # Verify file content
        with open(expected_path, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["post_slug"] == "test-post"
        assert len(saved_data["tweets"]) == 3
        assert saved_data["model_used"] == "google/gemini-2.5-flash-lite"
        assert "metadata" in saved_data
        assert saved_data["metadata"]["generator_version"] == "1.0.0"

    def test_save_thread_draft_with_backup(self):
        """Test thread draft saving creates backup of existing file."""
        output_manager = OutputManager(self.config)

        # Create initial draft
        draft_path = output_manager.save_thread_draft(self.sample_thread)
        initial_content = Path(draft_path).read_text()

        # Modify thread and save again
        self.sample_thread.engagement_score = 9.0
        draft_path_2 = output_manager.save_thread_draft(self.sample_thread)

        # Verify backup was created (backup files have timestamp in name)
        backup_files = list(self.generated_dir.glob("test-post-thread_backup_*.json"))
        assert len(backup_files) >= 1

        # Verify new content is different
        new_content = Path(draft_path_2).read_text()
        assert new_content != initial_content
        assert "9.0" in new_content  # New engagement score

    def test_commit_message_validation(self):
        """Test that commit messages are properly formatted."""
        # This test verifies commit message format without actual GitHub API calls
        output_manager = OutputManager(self.config)

        # Test PR body generation includes proper commit context
        pr_body = output_manager._create_pr_body(self.sample_thread, self.sample_post)

        # Verify PR body contains generation details that would be in commit
        assert "google/gemini-2.5-flash-lite" in pr_body
        assert "1.0" in pr_body  # prompt version
        assert "8.50" in pr_body  # engagement score

        # Verify structured format
        assert "## 🧵 Generated Tweet Thread" in pr_body
        assert "## 📋 Next Steps" in pr_body
        assert "## 🤖 Generation Details" in pr_body

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_pr_branch_naming_convention(self, mock_repo_info, mock_github):
        """Test that PR branches follow proper naming convention."""
        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_repo.owner.login = "testuser"
        mock_repo.get_pulls.return_value = []

        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch

        # Capture the branch name used in create_git_ref
        mock_repo.create_git_ref = Mock()
        mock_repo.create_file = Mock()

        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/testuser/test-repo/pull/1"
        mock_repo.create_pull.return_value = mock_pr
        mock_pr.add_to_assignees = Mock()
        mock_pr.add_to_labels = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test PR creation
        output_manager = OutputManager(self.config)
        output_manager.create_or_update_pr(self.sample_thread, self.sample_post)

        # Verify branch naming convention
        mock_repo.create_git_ref.assert_called_once()
        call_args = mock_repo.create_git_ref.call_args
        branch_ref = call_args[1]['ref']
        assert branch_ref == "refs/heads/tweet-thread/test-post"

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_pr_labels_and_assignment(self, mock_repo_info, mock_github):
        """Test that PRs are properly labeled and assigned."""
        # Setup mocks
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_repo.owner.login = "testuser"
        mock_repo.get_pulls.return_value = []

        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref = Mock()
        mock_repo.create_file = Mock()

        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/testuser/test-repo/pull/1"
        mock_repo.create_pull.return_value = mock_pr
        mock_pr.add_to_assignees = Mock()
        mock_pr.add_to_labels = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Test PR creation
        output_manager = OutputManager(self.config)
        output_manager.create_or_update_pr(self.sample_thread, self.sample_post)

        # Verify assignment and labeling
        mock_pr.add_to_assignees.assert_called_once_with("testuser")
        mock_pr.add_to_labels.assert_called_once_with("tweet-thread", "content", "review-needed")

    def test_invalid_batch_operations(self):
        """Test error handling for invalid batch operations."""
        output_manager = OutputManager(self.config)

        # Test invalid action
        invalid_operations = [
            {"action": "invalid_action", "path": "test.json", "content": "content"}
        ]

        with pytest.raises(GitHubAPIError) as exc_info:
            output_manager.batch_file_operations(invalid_operations, "Test commit")

        assert "Invalid action 'invalid_action'" in str(exc_info.value)

        # Test missing path
        invalid_operations = [
            {"action": "create", "content": "content"}
        ]

        with pytest.raises(GitHubAPIError) as exc_info:
            output_manager.batch_file_operations(invalid_operations, "Test commit")

        assert "File path is required" in str(exc_info.value)


class TestGitHubIntegrationEdgeCases:
    """Test edge cases and error scenarios for GitHub integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = GeneratorConfig(
            github_token="test_token",
            generated_directory=str(self.temp_dir / ".generated"),
            posted_directory=str(self.temp_dir / ".posted")
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_missing_github_token(self):
        """Test behavior when GitHub token is missing."""
        config_no_token = GeneratorConfig(
            github_token=None,
            generated_directory=str(self.temp_dir / ".generated"),
            posted_directory=str(self.temp_dir / ".posted")
        )

        output_manager = OutputManager(config_no_token)

        # Should handle missing token gracefully
        assert output_manager.github_client is None

    @patch('output_manager.get_repository_info')
    def test_missing_repository_info(self, mock_repo_info):
        """Test behavior when repository information is not available."""
        mock_repo_info.return_value = {}  # Empty repository info

        output_manager = OutputManager(self.config)

        with pytest.raises(GitHubAPIError) as exc_info:
            output_manager.get_repository_metadata()

        assert "Repository name not available" in str(exc_info.value)

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_repository_not_found(self, mock_repo_info, mock_github):
        """Test behavior when repository is not found."""
        mock_repo_info.return_value = {"repository": "nonexistent/repo"}

        mock_github_instance = Mock()
        mock_github_instance.get_repo.side_effect = Exception("Repository not found")
        mock_github.return_value = mock_github_instance

        output_manager = OutputManager(self.config)

        with pytest.raises(GitHubAPIError):
            output_manager.get_repository_metadata()

    @patch('output_manager.Github')
    @patch('output_manager.get_repository_info')
    def test_pr_creation_permission_denied(self, mock_repo_info, mock_github):
        """Test PR creation when permissions are insufficient."""
        mock_repo_info.return_value = {"repository": "testuser/test-repo"}

        mock_repo = Mock()
        mock_repo.create_pull.side_effect = Exception("Permission denied")
        mock_repo.get_pulls.return_value = []
        mock_repo.default_branch = "main"
        mock_repo.owner.login = "testuser"

        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref = Mock()
        mock_repo.create_file = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Create sample data
        sample_post = BlogPost(
            file_path="test.md", title="Test", content="content",
            frontmatter={}, canonical_url="http://test.com", slug="test"
        )
        sample_thread = ThreadData(
            post_slug="test", tweets=[], hook_variations=[],
            hashtags=[], model_used="test", style_profile_version="1.0"
        )

        output_manager = OutputManager(self.config)

        with pytest.raises(GitHubAPIError) as exc_info:
            output_manager.create_or_update_pr(sample_thread, sample_post)

        assert "Failed to create new PR" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])