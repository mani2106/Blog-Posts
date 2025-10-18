"""
Utility functions and helpers for the Tweet Thread Generator.

This module provides common functionality used across different components
of the system, including file operations, text processing, and validation helpers.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to create

    Returns:
        Path object for the directory
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def sanitize_slug_for_filename(slug: str) -> str:
    """
    Sanitize a slug for use in filenames and Git branch names.

    Replaces spaces and underscores with dashes, converts to lowercase,
    and removes any characters that are invalid for Git refs or filenames.

    Args:
        slug: The original slug string

    Returns:
        Sanitized slug safe for use in filenames and Git branch names
    """
    import re
    # Replace spaces and underscores with dashes, convert to lowercase
    sanitized = slug.replace(' ', '-').replace('_', '-').lower()
    # Remove any characters that aren't alphanumeric or dashes
    sanitized = re.sub(r'[^a-zA-Z0-9\-]', '', sanitized)
    return sanitized


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing problematic characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename string
    """
    # Replace problematic characters
    safe_chars = []
    for char in filename:
        if char.isalnum() or char in '-_.':
            safe_chars.append(char)
        elif char in ' /\\':
            safe_chars.append('-')

    # Join and clean up multiple dashes
    safe_name = ''.join(safe_chars)
    while '--' in safe_name:
        safe_name = safe_name.replace('--', '-')

    return safe_name.strip('-')


def load_json_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Safely load a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data or None if file doesn't exist or is invalid
    """
    path = Path(file_path)
    if not path.exists():
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load JSON file {path}: {e}")
        return None


def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    Safely save data to a JSON file.

    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation level

    Returns:
        True if successful, False otherwise
    """
    path = Path(file_path)
    ensure_directory(path.parent)

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        return True
    except (IOError, TypeError) as e:
        print(f"Error: Failed to save JSON file {path}: {e}")
        return False


def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """
    Calculate SHA-256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hexadecimal hash string
    """
    path = Path(file_path)
    if not path.exists():
        return ""

    hash_sha256 = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except IOError:
        return ""


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    if len(suffix) >= max_length:
        return text[:max_length]

    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing line endings.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove extra whitespace
    lines = []
    for line in text.split('\n'):
        lines.append(line.strip())

    # Remove empty lines at start and end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    return '\n'.join(lines)


def extract_slug_from_filename(filename: str) -> str:
    """
    Extract slug from blog post filename.

    Args:
        filename: Blog post filename (e.g., "2023-01-01-my-post.md")

    Returns:
        Slug string (e.g., "my-post")
    """
    # Remove extension
    name = Path(filename).stem

    # Remove date prefix if present (YYYY-MM-DD format)
    parts = name.split('-')
    if len(parts) >= 4 and len(parts[0]) == 4 and parts[0].isdigit():
        # Remove first 3 parts (year, month, day)
        slug_parts = parts[3:]
    else:
        slug_parts = parts

    return '-'.join(slug_parts)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format timestamp for logging and metadata.

    Args:
        dt: Datetime object, defaults to current time

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()

    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def count_words(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Text to count words in

    Returns:
        Word count
    """
    # Simple word counting - split on whitespace
    return len(text.split())


def count_sentences(text: str) -> int:
    """
    Count sentences in text.

    Args:
        text: Text to count sentences in

    Returns:
        Sentence count
    """
    # Simple sentence counting - count sentence-ending punctuation
    sentence_endings = ['.', '!', '?']
    count = 0

    for char in text:
        if char in sentence_endings:
            count += 1

    return max(1, count)  # At least 1 sentence


def validate_twitter_character_limit(text: str, limit: int = 280) -> bool:
    """
    Validate that text fits within Twitter character limit.

    Args:
        text: Text to validate
        limit: Character limit (default 280)

    Returns:
        True if within limit, False otherwise
    """
    return len(text) <= limit


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text.

    Args:
        text: Text to extract hashtags from

    Returns:
        List of hashtags (without # symbol)
    """
    import re

    # Find hashtags (# followed by word characters)
    hashtag_pattern = r'#(\w+)'
    matches = re.findall(hashtag_pattern, text)

    return matches


def is_github_actions_environment() -> bool:
    """
    Check if running in GitHub Actions environment.

    Returns:
        True if in GitHub Actions, False otherwise
    """
    return os.getenv("GITHUB_ACTIONS") == "true"


def get_repository_info() -> Dict[str, str]:
    """
    Get repository information from GitHub Actions environment.

    Returns:
        Dictionary with repository information
    """
    return {
        "repository": os.getenv("GITHUB_REPOSITORY", ""),
        "ref": os.getenv("GITHUB_REF", ""),
        "sha": os.getenv("GITHUB_SHA", ""),
        "actor": os.getenv("GITHUB_ACTOR", ""),
        "workflow": os.getenv("GITHUB_WORKFLOW", ""),
        "run_id": os.getenv("GITHUB_RUN_ID", ""),
        "run_number": os.getenv("GITHUB_RUN_NUMBER", "")
    }