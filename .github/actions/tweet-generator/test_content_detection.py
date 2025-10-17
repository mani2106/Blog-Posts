"""
Unit tests for content detection functionality.

This module tests git diff detection, frontmatter parsing, and content filtering logic
as specified in requirements 1.1, 1.2, and 1.3.
"""

import pytest
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_detector import ContentDetector
from models import BlogPost
from exceptions import ContentDetectionError


class TestContentDetector:
    """Test suite for ContentDetector class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.posts_dir = self.temp_dir / "_posts"
        self.notebooks_dir = self.temp_dir / "_notebooks"

        # Create directories
        self.posts_dir.mkdir(parents=True)
        self.notebooks_dir.mkdir(parents=True)

        # Initialize detector
        self.detector = ContentDetector(
            posts_dir=str(self.posts_dir),
            notebooks_dir=str(self.notebooks_dir)
        )

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_sample_markdown_post(self, filename: str, frontmatter: dict, content: str = "Sample content") -> Path:
        """Create a sample markdown blog post for testing."""
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

    def create_sample_notebook(self, filename: str, frontmatter: dict = None, cells: list = None) -> Path:
        """Create a sample Jupyter notebook for testing."""
        file_path = self.notebooks_dir / filename

        if cells is None:
            cells = []

        # Add frontmatter cell if provided
        if frontmatter:
            fm_lines = ["---\n"]
            for key, value in frontmatter.items():
                if isinstance(value, list):
                    fm_lines.append(f"{key}:\n")
                    for item in value:
                        fm_lines.append(f"  - {item}\n")
                elif isinstance(value, bool):
                    fm_lines.append(f"{key}: {str(value).lower()}\n")
                else:
                    fm_lines.append(f"{key}: {value}\n")
            fm_lines.append("---\n")

            frontmatter_cell = {
                "cell_type": "markdown",
                "source": fm_lines
            }
            cells.insert(0, frontmatter_cell)

        notebook = {
            "cells": cells,
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }

        file_path.write_text(json.dumps(notebook, indent=2), encoding='utf-8')
        return file_path


class TestGitDiffDetection(TestContentDetector):
    """Test git diff detection functionality (Requirement 1.1)."""

    @patch('subprocess.run')
    def test_detect_changed_posts_success(self, mock_run):
        """Test successful detection of changed blog posts."""
        # Create sample posts
        post1 = self.create_sample_markdown_post(
            "2024-01-01-test-post.md",
            {"title": "Test Post", "publish": True}
        )
        post2 = self.create_sample_markdown_post(
            "2024-01-02-draft-post.md",
            {"title": "Draft Post", "publish": False}
        )

        # Mock git diff output with correct path format
        mock_run.return_value = Mock(
            stdout=f"_posts/{post1.name}\n_posts/{post2.name}\n",
            returncode=0
        )

        # Change to temp directory for git operations and update detector paths
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(self.temp_dir)

            # Update detector to use relative paths from current directory
            self.detector.posts_dir = Path("_posts")
            self.detector.notebooks_dir = Path("_notebooks")

            changed_posts = self.detector.detect_changed_posts("main")

            # Should only return published post
            assert len(changed_posts) == 1
            assert changed_posts[0].title == "Test Post"
            assert changed_posts[0].frontmatter["publish"] is True

        finally:
            os.chdir(original_cwd)

    @patch('subprocess.run')
    def test_detect_changed_posts_no_changes(self, mock_run):
        """Test detection when no posts have changed."""
        # Mock empty git diff output
        mock_run.return_value = Mock(stdout="", returncode=0)

        changed_posts = self.detector.detect_changed_posts("main")
        assert len(changed_posts) == 0

    @patch('subprocess.run')
    def test_detect_changed_posts_git_error(self, mock_run):
        """Test handling of git command errors."""
        # Mock git command failure
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "diff"], stderr="fatal: not a git repository"
        )

        with pytest.raises(ContentDetectionError) as exc_info:
            self.detector.detect_changed_posts("main")

        assert "Git diff command failed" in str(exc_info.value)

    @patch('subprocess.run')
    def test_detect_changed_posts_filters_file_types(self, mock_run):
        """Test that only markdown and notebook files are processed."""
        # Create various file types
        md_post = self.create_sample_markdown_post(
            "2024-01-01-test.md",
            {"title": "MD Post", "publish": True}
        )

        nb_post = self.create_sample_notebook(
            "2024-01-01-test.ipynb",
            {"title": "NB Post", "publish": True}
        )

        # Create non-blog files
        (self.temp_dir / "README.md").write_text("# README")
        (self.temp_dir / "config.yml").write_text("config: value")

        # Mock git diff including all files
        mock_run.return_value = Mock(
            stdout=f"_posts/{md_post.name}\n"
                   f"_notebooks/{nb_post.name}\n"
                   f"README.md\n"
                   f"config.yml\n",
            returncode=0
        )

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(self.temp_dir)

            # Update detector to use relative paths from current directory
            self.detector.posts_dir = Path("_posts")
            self.detector.notebooks_dir = Path("_notebooks")

            changed_posts = self.detector.detect_changed_posts("main")

            # Should only return blog posts
            assert len(changed_posts) == 2
            titles = [post.title for post in changed_posts]
            assert "MD Post" in titles
            assert "NB Post" in titles

        finally:
            os.chdir(original_cwd)

    @patch('subprocess.run')
    def test_detect_changed_posts_handles_deleted_files(self, mock_run):
        """Test that deleted files are skipped gracefully."""
        # Mock git diff output with non-existent file
        mock_run.return_value = Mock(
            stdout="_posts/deleted-post.md\n_posts/existing-post.md\n",
            returncode=0
        )

        # Create only one of the files
        self.create_sample_markdown_post(
            "existing-post.md",
            {"title": "Existing Post", "publish": True}
        )

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(self.temp_dir)

            # Update detector to use relative paths from current directory
            self.detector.posts_dir = Path("_posts")
            self.detector.notebooks_dir = Path("_notebooks")

            changed_posts = self.detector.detect_changed_posts("main")

            # Should only return existing file
            assert len(changed_posts) == 1
            assert changed_posts[0].title == "Existing Post"

        finally:
            os.chdir(original_cwd)


class TestFrontmatterParsing(TestContentDetector):
    """Test frontmatter parsing with various formats (Requirement 1.2)."""

    def test_extract_frontmatter_markdown_basic(self):
        """Test basic frontmatter extraction from markdown."""
        frontmatter = {
            "title": "Test Post",
            "publish": True,
            "categories": ["tech", "tutorial"],
            "summary": "A test post"
        }

        post_file = self.create_sample_markdown_post("test.md", frontmatter)

        extracted = self.detector.extract_frontmatter(str(post_file))

        assert extracted["title"] == "Test Post"
        assert extracted["publish"] is True
        assert extracted["categories"] == ["tech", "tutorial"]
        assert extracted["summary"] == "A test post"

    def test_extract_frontmatter_markdown_various_types(self):
        """Test frontmatter with various data types."""
        frontmatter = {
            "title": "Complex Post",
            "publish": True,
            "auto_post": False,
            "date": "2024-01-01",
            "tags": ["python", "ai", "tutorial"],
            "rating": 4.5,
            "views": 1000
        }

        post_file = self.create_sample_markdown_post("complex.md", frontmatter)

        extracted = self.detector.extract_frontmatter(str(post_file))

        assert extracted["title"] == "Complex Post"
        assert extracted["publish"] is True
        assert extracted["auto_post"] is False
        # Date might be parsed as datetime object by frontmatter library
        assert str(extracted["date"]) == "2024-01-01"
        assert extracted["tags"] == ["python", "ai", "tutorial"]
        assert extracted["rating"] == 4.5
        assert extracted["views"] == 1000

    def test_extract_frontmatter_notebook_with_frontmatter_cell(self):
        """Test frontmatter extraction from notebook with frontmatter cell."""
        frontmatter = {
            "title": "Notebook Post",
            "publish": True,
            "categories": ["data-science"]
        }

        cells = [
            {
                "cell_type": "code",
                "source": ["print('Hello World')"]
            }
        ]

        nb_file = self.create_sample_notebook("test.ipynb", frontmatter, cells)

        extracted = self.detector.extract_frontmatter(str(nb_file))

        assert extracted["title"] == "Notebook Post"
        assert extracted["publish"] is True
        assert extracted["categories"] == ["data-science"]

    def test_extract_frontmatter_notebook_metadata_fallback(self):
        """Test frontmatter extraction from notebook metadata when no frontmatter cell."""
        nb_file = self.notebooks_dir / "metadata-test.ipynb"

        notebook = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": ["print('test')"]
                }
            ],
            "metadata": {
                "title": "Metadata Title",
                "tags": ["python", "notebook"],
                "description": "Test notebook description"
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        nb_file.write_text(json.dumps(notebook), encoding='utf-8')

        extracted = self.detector.extract_frontmatter(str(nb_file))

        assert extracted["title"] == "Metadata Title"
        assert extracted["categories"] == ["python", "notebook"]
        assert extracted["summary"] == "Test notebook description"

    def test_extract_frontmatter_empty_notebook(self):
        """Test frontmatter extraction from empty notebook."""
        nb_file = self.notebooks_dir / "empty.ipynb"

        notebook = {
            "cells": [],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }

        nb_file.write_text(json.dumps(notebook), encoding='utf-8')

        extracted = self.detector.extract_frontmatter(str(nb_file))

        assert extracted == {}

    def test_extract_frontmatter_file_not_found(self):
        """Test error handling for non-existent files."""
        with pytest.raises(ContentDetectionError) as exc_info:
            self.detector.extract_frontmatter("non-existent.md")

        assert "File not found" in str(exc_info.value)

    def test_extract_frontmatter_unsupported_file_type(self):
        """Test error handling for unsupported file types."""
        txt_file = self.temp_dir / "test.txt"
        txt_file.write_text("Some content")

        with pytest.raises(ContentDetectionError) as exc_info:
            self.detector.extract_frontmatter(str(txt_file))

        assert "Unsupported file type" in str(exc_info.value)

    def test_extract_frontmatter_malformed_yaml(self):
        """Test handling of malformed YAML frontmatter."""
        malformed_file = self.posts_dir / "malformed.md"
        malformed_content = """---
title: Test Post
publish: true
categories: [unclosed list
summary: Missing quote
---

Content here
"""
        malformed_file.write_text(malformed_content)

        # Should raise ContentDetectionError for malformed YAML
        with pytest.raises(ContentDetectionError):
            self.detector.extract_frontmatter(str(malformed_file))


class TestContentFiltering(TestContentDetector):
    """Test content filtering logic (Requirement 1.3)."""

    def test_should_process_post_publish_true(self):
        """Test that posts with publish: true are processed."""
        post = BlogPost(
            file_path="test.md",
            title="Test",
            content="Content",
            frontmatter={"publish": True},
            canonical_url="https://example.com/test",
            categories=[]
        )

        assert self.detector.should_process_post(post) is True

    def test_should_process_post_publish_false(self):
        """Test that posts with publish: false are not processed."""
        post = BlogPost(
            file_path="test.md",
            title="Test",
            content="Content",
            frontmatter={"publish": False},
            canonical_url="https://example.com/test",
            categories=[]
        )

        assert self.detector.should_process_post(post) is False

    def test_should_process_post_publish_missing(self):
        """Test that posts without publish flag are not processed."""
        post = BlogPost(
            file_path="test.md",
            title="Test",
            content="Content",
            frontmatter={"title": "Test"},
            canonical_url="https://example.com/test",
            categories=[]
        )

        assert self.detector.should_process_post(post) is False

    def test_should_process_post_publish_string_variations(self):
        """Test various string representations of publish flag."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("yes", True),
            ("Yes", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("no", False),
            ("0", False),
            ("invalid", False)
        ]

        for publish_value, expected in test_cases:
            post = BlogPost(
                file_path="test.md",
                title="Test",
                content="Content",
                frontmatter={"publish": publish_value},
                canonical_url="https://example.com/test",
                categories=[]
            )

            assert self.detector.should_process_post(post) is expected

    def test_should_process_post_publish_numeric_variations(self):
        """Test numeric representations of publish flag."""
        test_cases = [
            (1, True),
            (1.0, True),
            (0, False),
            (0.0, False),
            (-1, True),  # Any non-zero number is truthy
            (42, True)
        ]

        for publish_value, expected in test_cases:
            post = BlogPost(
                file_path="test.md",
                title="Test",
                content="Content",
                frontmatter={"publish": publish_value},
                canonical_url="https://example.com/test",
                categories=[]
            )

            assert self.detector.should_process_post(post) is expected


class TestBlogPostParsing(TestContentDetector):
    """Test complete blog post parsing functionality."""

    def test_parse_blog_post_markdown_complete(self):
        """Test parsing a complete markdown blog post."""
        frontmatter = {
            "title": "Complete Post",
            "publish": True,
            "auto_post": True,
            "categories": ["tech", "tutorial"],
            "summary": "A complete test post"
        }

        content = "# Introduction\n\nThis is a test post with content."
        post_file = self.create_sample_markdown_post("2024-01-01-complete.md", frontmatter, content)

        post = self.detector.parse_blog_post(post_file)

        assert post is not None
        assert post.title == "Complete Post"
        assert post.content == content
        assert post.categories == ["tech", "tutorial"]
        assert post.summary == "A complete test post"
        assert post.auto_post is True
        assert post.slug == "complete"
        assert "https://" in post.canonical_url

    def test_parse_blog_post_notebook_complete(self):
        """Test parsing a complete Jupyter notebook."""
        frontmatter = {
            "title": "Notebook Analysis",
            "publish": True,
            "categories": ["data-science"]
        }

        cells = [
            {
                "cell_type": "markdown",
                "source": ["# Data Analysis\n", "\n", "This notebook analyzes data."]
            },
            {
                "cell_type": "code",
                "source": ["import pandas as pd\n", "df = pd.read_csv('data.csv')"]
            }
        ]

        nb_file = self.create_sample_notebook("2024-01-01-analysis.ipynb", frontmatter, cells)

        post = self.detector.parse_blog_post(nb_file)

        assert post is not None
        assert post.title == "Notebook Analysis"
        assert "# Data Analysis" in post.content
        assert "```python" in post.content
        assert "import pandas as pd" in post.content
        assert post.categories == ["data-science"]
        assert post.slug == "analysis"

    def test_parse_blog_post_missing_title_uses_filename(self):
        """Test that missing title defaults to filename."""
        frontmatter = {"publish": True}

        post_file = self.create_sample_markdown_post("my-awesome-post.md", frontmatter)

        post = self.detector.parse_blog_post(post_file)

        assert post is not None
        assert post.title == "my-awesome-post"
        assert post.slug == "my-awesome-post"

    def test_parse_blog_post_categories_string_conversion(self):
        """Test that single category string is converted to list."""
        frontmatter = {
            "title": "Single Category",
            "publish": True,
            "categories": "technology"
        }

        post_file = self.create_sample_markdown_post("single-cat.md", frontmatter)

        post = self.detector.parse_blog_post(post_file)

        assert post is not None
        assert post.categories == ["technology"]

    def test_parse_blog_post_auto_post_string_conversion(self):
        """Test auto_post flag string conversion."""
        test_cases = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("1", True),
            ("0", False)
        ]

        for auto_post_value, expected in test_cases:
            frontmatter = {
                "title": "Auto Post Test",
                "publish": True,
                "auto_post": auto_post_value
            }

            post_file = self.create_sample_markdown_post(f"auto-{auto_post_value}.md", frontmatter)

            post = self.detector.parse_blog_post(post_file)

            assert post is not None
            assert post.auto_post is expected

    def test_parse_blog_post_nonexistent_file(self):
        """Test parsing non-existent file returns None."""
        non_existent = self.posts_dir / "does-not-exist.md"

        post = self.detector.parse_blog_post(non_existent)

        assert post is None

    def test_parse_blog_post_unsupported_extension(self):
        """Test parsing file with unsupported extension returns None."""
        txt_file = self.posts_dir / "test.txt"
        txt_file.write_text("Some content")

        post = self.detector.parse_blog_post(txt_file)

        assert post is None


class TestGetAllPosts(TestContentDetector):
    """Test getting all posts from directories."""

    def test_get_all_posts_mixed_content(self):
        """Test getting all posts from both directories."""
        # Create markdown posts
        self.create_sample_markdown_post(
            "2024-01-01-post1.md",
            {"title": "Post 1", "publish": True}
        )
        self.create_sample_markdown_post(
            "2024-01-02-post2.md",
            {"title": "Post 2", "publish": False}
        )

        # Create notebook posts
        self.create_sample_notebook(
            "2024-01-03-notebook1.ipynb",
            {"title": "Notebook 1", "publish": True}
        )

        all_posts = self.detector.get_all_posts()

        assert len(all_posts) == 3
        titles = [post.title for post in all_posts]
        assert "Post 1" in titles
        assert "Post 2" in titles
        assert "Notebook 1" in titles

    def test_get_all_posts_empty_directories(self):
        """Test getting posts from empty directories."""
        all_posts = self.detector.get_all_posts()

        assert len(all_posts) == 0

    def test_get_all_posts_missing_directories(self):
        """Test getting posts when directories don't exist."""
        # Remove directories
        shutil.rmtree(self.posts_dir)
        shutil.rmtree(self.notebooks_dir)

        all_posts = self.detector.get_all_posts()

        assert len(all_posts) == 0

    def test_get_all_posts_handles_invalid_files(self):
        """Test that invalid files are handled gracefully."""
        # Create valid post
        self.create_sample_markdown_post(
            "valid.md",
            {"title": "Valid Post", "publish": True}
        )

        # Create invalid files (these will still be parsed but with empty frontmatter)
        (self.posts_dir / "invalid.md").write_text("Invalid frontmatter content")
        (self.posts_dir / "empty.md").write_text("")

        all_posts = self.detector.get_all_posts()

        # Should return all files, but only valid one has proper frontmatter
        assert len(all_posts) == 3

        # Find the valid post
        valid_posts = [post for post in all_posts if post.title == "Valid Post"]
        assert len(valid_posts) == 1
        assert valid_posts[0].frontmatter.get("publish") is True

        # Invalid files should have empty or minimal frontmatter
        invalid_posts = [post for post in all_posts if post.title != "Valid Post"]
        for post in invalid_posts:
            assert post.frontmatter.get("publish") is None or post.frontmatter.get("publish") is False


class TestContentParsing(TestContentDetector):
    """Test content parsing from different file types."""

    def test_parse_markdown_content_basic(self):
        """Test parsing content from markdown file."""
        frontmatter = {"title": "Test", "publish": True}
        content = "# Header\n\nParagraph with **bold** text.\n\n- List item 1\n- List item 2"

        post_file = self.create_sample_markdown_post("content-test.md", frontmatter, content)

        parsed_content = self.detector._parse_markdown_content(post_file)

        assert parsed_content == content

    def test_parse_notebook_content_mixed_cells(self):
        """Test parsing content from notebook with mixed cell types."""
        cells = [
            {
                "cell_type": "markdown",
                "source": ["# Analysis Report\n", "\n", "This notebook contains analysis."]
            },
            {
                "cell_type": "code",
                "source": ["import numpy as np\n", "data = np.array([1, 2, 3])"]
            },
            {
                "cell_type": "markdown",
                "source": ["## Results\n", "\n", "The analysis shows interesting patterns."]
            },
            {
                "cell_type": "code",
                "source": ["print(data.mean())"]
            }
        ]

        nb_file = self.create_sample_notebook("analysis.ipynb", cells=cells)

        content = self.detector._parse_notebook_content(nb_file)

        # Should contain markdown content
        assert "# Analysis Report" in content
        assert "## Results" in content

        # Should contain code blocks
        assert "```python" in content
        assert "import numpy as np" in content
        assert "print(data.mean())" in content

    def test_parse_notebook_content_with_frontmatter_cell(self):
        """Test parsing notebook content that starts with frontmatter."""
        frontmatter = {"title": "Test Notebook", "publish": True}

        cells = [
            {
                "cell_type": "markdown",
                "source": ["## Introduction\n", "\n", "This is the actual content."]
            }
        ]

        nb_file = self.create_sample_notebook("frontmatter-test.ipynb", frontmatter, cells)

        content = self.detector._parse_notebook_content(nb_file)

        # Should not include frontmatter in content
        assert "title: Test Notebook" not in content
        assert "## Introduction" in content
        assert "This is the actual content." in content

    def test_parse_notebook_content_empty_cells_skipped(self):
        """Test that empty cells are skipped during parsing."""
        cells = [
            {
                "cell_type": "markdown",
                "source": ["# Title"]
            },
            {
                "cell_type": "code",
                "source": [""]  # Empty cell
            },
            {
                "cell_type": "markdown",
                "source": ["   \n  \n  "]  # Whitespace only
            },
            {
                "cell_type": "code",
                "source": ["print('hello')"]
            }
        ]

        nb_file = self.create_sample_notebook("empty-cells.ipynb", cells=cells)

        content = self.detector._parse_notebook_content(nb_file)

        # Should contain non-empty content
        assert "# Title" in content
        assert "print('hello')" in content

        # Should not have excessive whitespace from empty cells
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) >= 2  # At least title and code


class TestEdgeCases(TestContentDetector):
    """Test edge cases and error conditions."""

    def test_detect_changed_posts_with_spaces_in_filenames(self):
        """Test handling of filenames with spaces."""
        # Create post with spaces in filename
        post_file = self.create_sample_markdown_post(
            "2024-01-01-post with spaces.md",
            {"title": "Spaced Post", "publish": True}
        )

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=f"_posts/{post_file.name}\n",
                returncode=0
            )

            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(self.temp_dir)
                self.detector.posts_dir = Path("_posts")
                self.detector.notebooks_dir = Path("_notebooks")

                changed_posts = self.detector.detect_changed_posts("main")

                assert len(changed_posts) == 1
                assert changed_posts[0].title == "Spaced Post"

            finally:
                os.chdir(original_cwd)

    def test_extract_frontmatter_unicode_content(self):
        """Test frontmatter extraction with unicode characters."""
        frontmatter = {
            "title": "Unicode Test 🚀",
            "publish": True,
            "summary": "Testing with émojis and spëcial chars"
        }

        post_file = self.create_sample_markdown_post("unicode.md", frontmatter)

        extracted = self.detector.extract_frontmatter(str(post_file))

        assert extracted["title"] == "Unicode Test 🚀"
        assert extracted["summary"] == "Testing with émojis and spëcial chars"

    def test_parse_blog_post_very_long_content(self):
        """Test parsing blog post with very long content."""
        frontmatter = {"title": "Long Post", "publish": True}

        # Create very long content
        long_content = "This is a test. " * 1000  # 16,000 characters

        post_file = self.create_sample_markdown_post("long.md", frontmatter, long_content)

        post = self.detector.parse_blog_post(post_file)

        assert post is not None
        assert post.title == "Long Post"
        assert len(post.content) > 15000

    def test_should_process_post_edge_case_values(self):
        """Test publish flag with edge case values."""
        edge_cases = [
            (None, False),
            ("", False),
            ([], False),
            ({}, False),
            ("True", True),
            ("FALSE", False),
            (2.5, True),  # Non-zero float
            (0.0, False)  # Zero float
        ]

        for publish_value, expected in edge_cases:
            post = BlogPost(
                file_path="test.md",
                title="Test",
                content="Content",
                frontmatter={"publish": publish_value},
                canonical_url="https://example.com/test",
                categories=[]
            )

            result = self.detector.should_process_post(post)
            assert result is expected, f"Failed for publish_value: {publish_value}"

    def test_parse_notebook_with_output_cells(self):
        """Test parsing notebook that includes output cells."""
        cells = [
            {
                "cell_type": "code",
                "source": ["print('Hello World')"],
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": ["Hello World\n"]
                    }
                ]
            },
            {
                "cell_type": "markdown",
                "source": ["## Results\nThe output was successful."]
            }
        ]

        nb_file = self.create_sample_notebook(
            "with-outputs.ipynb",
            {"title": "Output Test", "publish": True},
            cells
        )

        post = self.detector.parse_blog_post(nb_file)

        assert post is not None
        assert post.title == "Output Test"
        assert "print('Hello World')" in post.content
        assert "## Results" in post.content
        # Output cells should not be included in content
        assert "Hello World\n" not in post.content

    def test_extract_frontmatter_notebook_complex_metadata(self):
        """Test notebook with complex metadata structure."""
        nb_file = self.notebooks_dir / "complex-metadata.ipynb"

        notebook = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                },
                "title": "Complex Notebook",
                "tags": ["machine-learning", "data-analysis"],
                "description": "Advanced data analysis notebook",
                "custom_field": "custom_value"
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        nb_file.write_text(json.dumps(notebook), encoding='utf-8')

        extracted = self.detector.extract_frontmatter(str(nb_file))

        assert extracted["title"] == "Complex Notebook"
        assert extracted["categories"] == ["machine-learning", "data-analysis"]
        assert extracted["summary"] == "Advanced data analysis notebook"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])