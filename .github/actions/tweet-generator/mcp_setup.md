# GitHub MCP Tools Setup

The GitHub Tweet Thread Generator uses GitHub API for PR creation and repository operations. GitHub MCP tools can be helpful for testing and development.

## Recommended MCP Tools

### 1. GitHub MCP Server

Add this to your `.kiro/settings/mcp.json` (workspace level) or `~/.kiro/settings/mcp.json` (user level):

```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token-here"
      },
      "disabled": false,
      "autoApprove": [
        "create_repository",
        "get_repository",
        "list_repositories",
        "create_issue",
        "get_issue",
        "list_issues",
        "create_pull_request",
        "get_pull_request",
        "list_pull_requests"
      ]
    }
  }
}
```

### 2. File System MCP Server (for testing file operations)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "--base-directory", "."],
      "disabled": false,
      "autoApprove": [
        "read_file",
        "write_file",
        "create_directory",
        "list_directory"
      ]
    }
  }
}
```

## Installation

### Prerequisites

Install `uv` and `uvx` (Python package manager):

```bash
# On macOS/Linux with curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows with PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv

# Or with homebrew (macOS)
brew install uv
```

### Setup GitHub Token

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Create a new token with these permissions:
   - `repo` (Full control of private repositories)
   - `pull_requests` (Read/write pull requests)
   - `issues` (Read/write issues)
3. Add the token to your MCP configuration

## Usage Examples

Once configured, you can use MCP tools in Kiro to:

### Test Repository Operations

```python
# Test getting repository information
repo_info = mcp_github.get_repository("owner/repo-name")

# Test creating a pull request (useful for testing PR creation logic)
pr = mcp_github.create_pull_request(
    owner="owner",
    repo="repo-name",
    title="Test PR",
    body="Test PR body",
    head="feature-branch",
    base="main"
)
```

### Test File Operations

```python
# Test reading generated files
content = mcp_filesystem.read_file(".generated/test-thread.json")

# Test creating directories
mcp_filesystem.create_directory("test_output")
```

### Validate GitHub Integration

```python
# Test the actual GitHub client used by the tweet generator
from github import Github

github_client = Github("your-token")
repo = github_client.get_repo("owner/repo-name")

# Test PR creation (matches what OutputManager does)
pr = repo.create_pull(
    title="Tweet Thread: Test Post",
    body="Generated tweet thread for review",
    head="tweet-threads",
    base="main"
)
```

## Benefits for Testing

1. **API Testing**: Test GitHub API calls without modifying your actual repository
2. **Integration Testing**: Validate the complete workflow including GitHub operations
3. **Debugging**: Inspect GitHub API responses and troubleshoot issues
4. **Development**: Prototype new GitHub features before implementing them

## Alternative: Mock Testing

If you prefer not to use MCP tools, you can mock GitHub API calls in tests:

```python
# In test files
from unittest.mock import Mock, patch

@patch('github.Github')
def test_pr_creation(mock_github):
    # Mock GitHub client
    mock_repo = Mock()
    mock_github.return_value.get_repo.return_value = mock_repo

    # Test your code
    output_manager = OutputManager(config)
    result = output_manager.create_or_update_pr(thread_data, blog_post)

    # Verify GitHub API was called correctly
    mock_repo.create_pull.assert_called_once()
```

## Troubleshooting

### MCP Server Not Found

```bash
# Check if uvx is installed
uvx --version

# Install MCP server manually
uvx install mcp-server-github
```

### Token Issues

- Ensure your GitHub token has the correct permissions
- Check that the token is not expired
- Verify the token is correctly set in the MCP configuration

### Connection Issues

- Check your internet connection
- Verify GitHub API is accessible
- Try testing with a simple GitHub API call first

## Testing Integration

Add MCP-based tests to your test suite:

```python
# test_github_integration.py
def test_github_mcp_integration():
    """Test GitHub operations using MCP tools."""
    # This would use MCP tools to test GitHub integration
    # without affecting your actual repository
    pass
```

This setup will give you powerful tools for testing and developing GitHub integrations!