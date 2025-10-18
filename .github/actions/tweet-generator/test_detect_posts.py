#!/usr/bin/env python3
"""
Test script to verify detect_changed_posts method works correctly.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_detector import ContentDetector


def test_detect_changed_posts():
    """Test the detect_changed_posts method."""
    print("🧪 Testing detect_changed_posts method...")

    detector = ContentDetector()

    try:
        # Test with main branch
        changed_posts = detector.detect_changed_posts(base_branch="main")

        print(f"✅ detect_changed_posts completed successfully")
        print(f"📝 Found {len(changed_posts)} changed posts")

        for i, post in enumerate(changed_posts):
            print(f"   {i+1}. {post.title} ({post.file_path})")
            print(f"      Categories: {post.categories}")
            print(f"      Auto-post: {post.auto_post}")
            print(f"      Publish flag: {post.frontmatter.get('publish', False)}")

        return True

    except Exception as e:
        print(f"❌ detect_changed_posts failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_all_posts():
    """Test the get_all_posts method."""
    print("\n🧪 Testing get_all_posts method...")

    detector = ContentDetector()

    try:
        all_posts = detector.get_all_posts()

        print(f"✅ get_all_posts completed successfully")
        print(f"📝 Found {len(all_posts)} total posts")

        # Show posts with publish: true
        publishable_posts = [post for post in all_posts if detector.should_process_post(post)]
        print(f"📤 Found {len(publishable_posts)} publishable posts (with publish: true)")

        for i, post in enumerate(publishable_posts):
            print(f"   {i+1}. {post.title}")
            print(f"      File: {Path(post.file_path).name}")
            print(f"      Categories: {post.categories}")

        return True

    except Exception as e:
        print(f"❌ get_all_posts failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 Starting ContentDetector method tests...\n")

    success = True

    try:
        success &= test_detect_changed_posts()
        success &= test_get_all_posts()

        if success:
            print("\n✅ All method tests passed! ContentDetector is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed.")
            return 1

    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())