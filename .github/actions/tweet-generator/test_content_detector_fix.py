#!/usr/bin/env python3
"""
Test script to verify content detector path resolution fixes.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_detector import ContentDetector


def test_content_detector_initialization():
    """Test that ContentDetector initializes correctly with path resolution."""
    print("🧪 Testing ContentDetector initialization...")

    # Test with default parameters
    detector = ContentDetector()

    print(f"✅ Repository root detected: {detector.repo_root}")
    print(f"✅ Posts directory: {detector.posts_dir}")
    print(f"✅ Notebooks directory: {detector.notebooks_dir}")

    # Verify paths are absolute
    assert detector.repo_root.is_absolute(), "Repository root should be absolute path"
    assert detector.posts_dir.is_absolute(), "Posts directory should be absolute path"
    assert detector.notebooks_dir.is_absolute(), "Notebooks directory should be absolute path"

    print("✅ All paths are absolute")

    # Test with explicit repo root
    explicit_root = Path.cwd()
    detector2 = ContentDetector(repo_root=str(explicit_root))

    assert detector2.repo_root == explicit_root.resolve(), "Explicit repo root should match"
    print("✅ Explicit repo root works correctly")

    return True


def test_path_resolution():
    """Test that paths are resolved correctly relative to repo root."""
    print("\n🧪 Testing path resolution...")

    detector = ContentDetector()

    # Check if posts directory exists (it should in this repo)
    posts_exist = detector.posts_dir.exists()
    notebooks_exist = detector.notebooks_dir.exists()

    print(f"📁 Posts directory exists: {posts_exist}")
    print(f"📓 Notebooks directory exists: {notebooks_exist}")

    if posts_exist:
        # List some files in posts directory
        post_files = list(detector.posts_dir.glob("*.md"))
        print(f"📝 Found {len(post_files)} markdown files in posts directory")
        for post_file in post_files[:3]:  # Show first 3
            print(f"   • {post_file.name}")

    if notebooks_exist:
        # List some files in notebooks directory
        notebook_files = list(detector.notebooks_dir.glob("*.ipynb"))
        print(f"📓 Found {len(notebook_files)} notebook files in notebooks directory")
        for notebook_file in notebook_files[:3]:  # Show first 3
            print(f"   • {notebook_file.name}")

    return True


def test_environment_detection():
    """Test environment detection capabilities."""
    print("\n🧪 Testing environment detection...")

    print(f"🏠 Current working directory: {Path.cwd()}")
    print(f"🔧 GITHUB_WORKSPACE: {os.environ.get('GITHUB_WORKSPACE', 'Not set')}")
    print(f"🔧 GITHUB_ACTIONS: {os.environ.get('GITHUB_ACTIONS', 'Not set')}")

    # Test repo root detection
    detector = ContentDetector()
    repo_root = detector._find_repo_root()

    print(f"🔍 Detected repo root: {repo_root}")

    # Verify .git directory exists in repo root
    git_dir = repo_root / ".git"
    print(f"📁 .git directory exists: {git_dir.exists()}")

    return True


def main():
    """Run all tests."""
    print("🚀 Starting ContentDetector path resolution tests...\n")

    try:
        test_content_detector_initialization()
        test_path_resolution()
        test_environment_detection()

        print("\n✅ All tests passed! ContentDetector path resolution is working correctly.")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())