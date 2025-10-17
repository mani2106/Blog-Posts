#!/usr/bin/env python3
"""
Dependency installer for GitHub Tweet Thread Generator.

This script installs all required dependencies for the project.
"""

import sys
import subprocess
import os
from pathlib import Path

def install_requirements():
    """Install requirements from requirements.txt."""
    project_root = Path(__file__).parent
    requirements_file = project_root / "requirements.txt"

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    print("📦 Installing dependencies from requirements.txt...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_dev_dependencies():
    """Install development dependencies."""
    dev_deps = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0"
    ]

    print("🔧 Installing development dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install"
        ] + dev_deps, check=True)
        print("✓ Development dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dev dependencies: {e}")
        return False

def verify_installation():
    """Verify that key packages are installed."""
    required_packages = [
        'httpx', 'pydantic', 'PyGithub', 'tweepy', 'pyyaml',
        'nltk', 'textstat', 'emoji', 'pytest'
    ]

    print("🔍 Verifying installation...")
    failed = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed.append(package)

    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False
    else:
        print("\n✅ All packages verified successfully!")
        return True

def setup_nltk_data():
    """Download required NLTK data."""
    try:
        import nltk
        print("📚 Downloading NLTK data...")

        # Download required NLTK data
        nltk_downloads = ['punkt', 'stopwords', 'vader_lexicon', 'averaged_perceptron_tagger']

        for item in nltk_downloads:
            try:
                nltk.download(item, quiet=True)
                print(f"✓ Downloaded {item}")
            except Exception as e:
                print(f"⚠️  Could not download {item}: {e}")

        return True
    except ImportError:
        print("⚠️  NLTK not available, skipping data download")
        return False

def main():
    """Main installation process."""
    print("🚀 GitHub Tweet Thread Generator - Dependency Installer")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return 1

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Install main dependencies
    if not install_requirements():
        return 1

    # Install dev dependencies
    install_dev = input("\nInstall development dependencies? (y/N): ").strip().lower()
    if install_dev in ['y', 'yes']:
        install_dev_dependencies()

    # Verify installation
    if not verify_installation():
        return 1

    # Setup NLTK data
    setup_nltk = input("\nDownload NLTK data? (Y/n): ").strip().lower()
    if setup_nltk not in ['n', 'no']:
        setup_nltk_data()

    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Run 'python run_tests.py setup' to test basic functionality")
    print("2. Run 'python run_tests.py monitoring' to test monitoring system")
    print("3. Check README.md for usage instructions")

    return 0

if __name__ == "__main__":
    sys.exit(main())