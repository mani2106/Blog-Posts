"""
Content detection and blog post processing for the Tweet Thread Generator.

This module handles detecting changed blog posts from git diff analysis,
extracting frontmatter metadata, and filtering posts for processing.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter

from models import BlogPost
from exceptions import ContentDetectionError
from utils import extract_slug_from_filename


class ContentDetector:
    """Detects and processes blog post content for tweet generation."""

    def __init__(self, posts_dir: str = "_posts", notebooks_dir: str = "_notebooks"):
        """
        Initialize content detector.

        Args:
            posts_dir: Directory containing markdown blog posts
            notebooks_dir: Directory containing Jupyter notebook posts
        """
        self.posts_dir = Path(posts_dir)
        self.notebooks_dir = Path(notebooks_dir)

    def detect_changed_posts(self, base_branch: str = "main") -> List[BlogPost]:
        """
        Detect changed blog posts using git diff analysis.

        Args:
            base_branch: Base branch to compare against

        Returns:
            List of BlogPost objects for changed posts

        Raises:
            ContentDetectionError: If git operations fail
        """
        try:
            # Get list of changed files using git diff
            cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

            # Filter for blog post files
            blog_post_files = []
            for file_path in changed_files:
                path = Path(file_path)
                # Check if file is in posts or notebooks directory and has correct extension
                if ((path.parent == self.posts_dir and path.suffix == '.md') or
                    (path.parent == self.notebooks_dir and path.suffix == '.ipynb')):
                    if path.exists():  # Only process files that still exist
                        blog_post_files.append(path)

            # Parse each changed blog post
            changed_posts = []
            for file_path in blog_post_files:
                try:
                    post = self.parse_blog_post(file_path)
                    if post and self.should_process_post(post):
                        changed_posts.append(post)
                except Exception as e:
                    print(f"Warning: Failed to parse {file_path}: {e}")
                    continue

            return changed_posts

        except subprocess.CalledProcessError as e:
            raise ContentDetectionError(
                f"Git diff command failed: {e}",
                {"command": cmd, "returncode": e.returncode, "stderr": e.stderr}
            )
        except Exception as e:
            raise ContentDetectionError(f"Failed to detect changed posts: {e}")

    def extract_frontmatter(self, file_path: str) -> Dict[str, Any]:
        """
        Extract frontmatter metadata from a blog post file.

        Args:
            file_path: Path to the blog post file

        Returns:
            Dictionary containing frontmatter data

        Raises:
            ContentDetectionError: If frontmatter parsing fails
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise ContentDetectionError(f"File not found: {file_path}")

            if file_path.suffix == '.md':
                # Parse markdown file with frontmatter
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                return post.metadata

            elif file_path.suffix == '.ipynb':
                # Parse Jupyter notebook metadata
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)

                # Extract metadata from notebook
                metadata = {}

                # Check for frontmatter in first cell if it's markdown
                if (notebook.get('cells') and
                    len(notebook['cells']) > 0 and
                    notebook['cells'][0].get('cell_type') == 'markdown'):

                    first_cell_source = ''.join(notebook['cells'][0].get('source', []))

                    # Try to parse frontmatter from first cell
                    if first_cell_source.strip().startswith('---'):
                        try:
                            post = frontmatter.loads(first_cell_source)
                            metadata = post.metadata
                        except Exception:
                            # If frontmatter parsing fails, extract from notebook metadata
                            pass

                # Fallback to notebook-level metadata
                if not metadata:
                    nb_metadata = notebook.get('metadata', {})
                    # Extract common fields from notebook metadata
                    if 'title' in nb_metadata:
                        metadata['title'] = nb_metadata['title']
                    if 'tags' in nb_metadata:
                        metadata['categories'] = nb_metadata['tags']
                    if 'description' in nb_metadata:
                        metadata['summary'] = nb_metadata['description']

                return metadata

            else:
                raise ContentDetectionError(f"Unsupported file type: {file_path.suffix}")

        except Exception as e:
            if isinstance(e, ContentDetectionError):
                raise
            raise ContentDetectionError(
                f"Failed to extract frontmatter from {file_path}: {e}",
                {"file_path": str(file_path), "error_type": type(e).__name__}
            )

    def should_process_post(self, post: BlogPost) -> bool:
        """
        Determine if a blog post should be processed for tweet generation.

        Args:
            post: BlogPost object to evaluate

        Returns:
            True if post should be processed, False otherwise
        """
        # Check if post has publish: true flag in frontmatter
        publish_flag = post.frontmatter.get('publish', False)

        # Handle different ways the publish flag might be specified
        if isinstance(publish_flag, str):
            publish_flag = publish_flag.lower() in ('true', 'yes', '1')
        elif isinstance(publish_flag, (int, float)):
            publish_flag = bool(publish_flag)

        return bool(publish_flag)

    def parse_blog_post(self, file_path: Path) -> Optional[BlogPost]:
        """
        Parse a blog post file into a BlogPost object.

        Args:
            file_path: Path to the blog post file

        Returns:
            BlogPost object or None if parsing fails
        """
        try:
            if not file_path.exists():
                return None

            # Extract frontmatter metadata
            frontmatter_data = self.extract_frontmatter(str(file_path))

            # Extract content based on file type
            content = ""
            if file_path.suffix == '.md':
                content = self._parse_markdown_content(file_path)
            elif file_path.suffix == '.ipynb':
                content = self._parse_notebook_content(file_path)
            else:
                return None

            # Extract required fields from frontmatter
            title = frontmatter_data.get('title', file_path.stem)
            categories = frontmatter_data.get('categories', [])
            if isinstance(categories, str):
                categories = [categories]

            summary = frontmatter_data.get('summary') or frontmatter_data.get('description')
            auto_post = frontmatter_data.get('auto_post', False)

            # Handle auto_post flag conversion
            if isinstance(auto_post, str):
                auto_post = auto_post.lower() in ('true', 'yes', '1')
            elif isinstance(auto_post, (int, float)):
                auto_post = bool(auto_post)

            # Generate canonical URL (this would typically be based on site config)
            slug = extract_slug_from_filename(file_path.name)
            canonical_url = f"https://example.com/{slug}/"  # Placeholder - should be configurable

            return BlogPost(
                file_path=str(file_path),
                title=title,
                content=content,
                frontmatter=frontmatter_data,
                canonical_url=canonical_url,
                categories=categories,
                summary=summary,
                auto_post=auto_post,
                slug=slug
            )

        except Exception as e:
            print(f"Warning: Failed to parse blog post {file_path}: {e}")
            return None

    def get_all_posts(self) -> List[BlogPost]:
        """
        Get all blog posts from posts and notebooks directories.

        Returns:
            List of all BlogPost objects
        """
        all_posts = []

        # Process markdown posts from _posts directory
        if self.posts_dir.exists():
            for md_file in self.posts_dir.glob('*.md'):
                post = self.parse_blog_post(md_file)
                if post:
                    all_posts.append(post)

        # Process Jupyter notebooks from _notebooks directory
        if self.notebooks_dir.exists():
            for nb_file in self.notebooks_dir.glob('*.ipynb'):
                post = self.parse_blog_post(nb_file)
                if post:
                    all_posts.append(post)

        return all_posts

    def _parse_markdown_content(self, file_path: Path) -> str:
        """
        Parse content from a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Content string without frontmatter
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            return post.content
        except Exception as e:
            print(f"Warning: Failed to parse markdown content from {file_path}: {e}")
            return ""

    def _parse_notebook_content(self, file_path: Path) -> str:
        """
        Parse content from a Jupyter notebook file.

        Args:
            file_path: Path to notebook file

        Returns:
            Combined content from all cells
        """
        try:
            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            content_parts = []

            for cell in notebook.get('cells', []):
                cell_type = cell.get('cell_type', '')
                source = cell.get('source', [])

                if isinstance(source, list):
                    cell_content = ''.join(source)
                else:
                    cell_content = str(source)

                # Skip empty cells
                if not cell_content.strip():
                    continue

                # For markdown cells, add content directly
                if cell_type == 'markdown':
                    # Skip frontmatter in first cell if present
                    if (len(content_parts) == 0 and
                        cell_content.strip().startswith('---')):
                        # Try to extract content after frontmatter
                        try:
                            post = frontmatter.loads(cell_content)
                            if post.content.strip():
                                content_parts.append(post.content)
                        except Exception:
                            # If frontmatter parsing fails, include the whole cell
                            content_parts.append(cell_content)
                    else:
                        content_parts.append(cell_content)

                # For code cells, add code with markdown formatting
                elif cell_type == 'code':
                    content_parts.append(f"```python\n{cell_content}\n```")

            return '\n\n'.join(content_parts)

        except Exception as e:
            print(f"Warning: Failed to parse notebook content from {file_path}: {e}")
            return ""