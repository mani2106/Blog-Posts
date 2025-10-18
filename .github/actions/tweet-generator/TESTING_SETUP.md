# Testing Setup Guide

This guide helps you set up the testing environment for the GitHub Tweet Thread Generator.

## Quick Start

### 1. Install Dependencies

```bash
# Navigate to the tweet generator directory
cd .github/actions/tweet-generator

# Install dependencies (recommended)
python install_dependencies.py

# OR manually install requirements
pip install -r requirements.txt
```

### 2. Run Tests

```bash
# Run the simple test runner
python run_tests.py

# OR run specific tests
python run_tests.py setup           # Basic setup tests
python run_tests.py monitoring      # Full monitoring tests
python run_tests.py monitoring-minimal  # Minimal monitoring tests

# OR run individual test files directly
python test_setup.py               # Basic setup verification
python test_monitoring_simple.py   # Simple monitoring tests
```

## Detailed Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for repository operations)

### Step-by-Step Setup

#### 1. Check Python Version

```bash
python --version
# Should show Python 3.8 or higher
```

#### 2. Install Core Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Key packages that will be installed:
# - httpx (HTTP client)
# - pydantic (data validation)
# - PyGithub (GitHub API)
# - tweepy (Twitter API)
# - nltk (text processing)
# - pytest (testing framework)
```

#### 3. Install Development Dependencies (Optional)

```bash
pip install pytest pytest-asyncio black flake8 mypy
```

#### 4. Setup NLTK Data (Required for text analysis)

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')
```

#### 5. Verify Installation

```bash
python test_setup.py
```

## Testing Options

### Option 1: Automated Test Runner (Recommended)

```bash
# Interactive test runner
python run_tests.py

# Direct test selection
python run_tests.py setup
python run_tests.py monitoring
python run_tests.py all
```

### Option 2: Individual Test Files

```bash
# Basic setup and imports
python test_setup.py

# Simple monitoring tests
python test_monitoring_simple.py

# Full monitoring system tests
python test_monitoring.py

# Auto-posting functionality
python test_auto_posting.py
```

### Option 3: Pytest (Advanced)

```bash
# Install the package in development mode
pip install -e .

# Run with pytest
pytest test_*.py -v

# Run specific test categories
pytest -m monitoring -v
pytest -m unit -v
```

## Common Issues and Solutions

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Use the test runner which handles paths automatically
python run_tests.py

# OR set PYTHONPATH manually
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python test_monitoring.py
```

### Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'httpx'`

**Solution**:
```bash
# Install missing dependencies
python install_dependencies.py

# OR install manually
pip install httpx pydantic PyGithub tweepy nltk textstat emoji
```

### NLTK Data Missing

**Problem**: `LookupError: Resource punkt not found`

**Solution**:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')
```

### Permission Issues

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Install with user flag
pip install --user -r requirements.txt

# OR use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables for Testing

```bash
# Optional: Set test environment variables
export OPENROUTER_API_KEY="test-key"
export DRY_RUN="true"
export LOG_LEVEL="DEBUG"

# Run tests with environment
python run_tests.py monitoring
```

## Test Output Structure

```
test_output/
├── test-metrics-report.json      # Metrics test results
├── test-dashboard-report.json    # Dashboard test results
└── test-logs/                    # Test execution logs
```

## Continuous Integration Setup

For GitHub Actions or other CI systems:

```yaml
# .github/workflows/test.yml
name: Test Tweet Generator
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd .github/actions/tweet-generator
          python install_dependencies.py

      - name: Run tests
        run: |
          cd .github/actions/tweet-generator
          python run_tests.py all
```

## Package Management Best Practices

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv tweet-generator-env

# Activate (Linux/Mac)
source tweet-generator-env/bin/activate

# Activate (Windows)
tweet-generator-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Development Installation

```bash
# Install package in editable mode
pip install -e .

# This allows importing the package from anywhere
python -c "from src.monitoring import setup_monitoring; print('Success!')"
```

### Dependency Management

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Install exact versions
pip install -r requirements.txt

# Upgrade packages
pip install --upgrade -r requirements.txt
```

## Troubleshooting

### Windows-Specific Issues

```cmd
# Use Python launcher
py -3 install_dependencies.py
py -3 run_tests.py setup

# Set PYTHONPATH on Windows
set PYTHONPATH=%PYTHONPATH%;%CD%\src
python test_monitoring.py
```

### macOS/Linux-Specific Issues

```bash
# Use python3 explicitly
python3 install_dependencies.py
python3 run_tests.py setup

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Getting Help

1. **Check the logs**: Test output includes detailed error information
2. **Verify dependencies**: Run `python install_dependencies.py`
3. **Check Python path**: Ensure `src` directory is accessible
4. **Review requirements**: Make sure all packages in `requirements.txt` are installed
5. **Use test runner**: The `run_tests.py` script handles most setup automatically

## Next Steps

After successful testing setup:

1. Run `python run_tests.py setup` to verify basic functionality
2. Run `python run_tests.py monitoring` to test the monitoring system
3. Check the generated reports in `test_output/` directory
4. Review the main README.md for usage instructions