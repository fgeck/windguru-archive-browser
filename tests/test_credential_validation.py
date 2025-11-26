"""
Tests for credential validation logic.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.cli.app import WindguruCLI
from src.models.auth import AuthCredentials


class TestCredentialValidation:
    """Tests for credential validation in CLI app."""

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    @patch('src.cli.app.CredentialStorage')
    def test_cached_credentials_valid(self, mock_storage, mock_auth_service_class, mock_prompt):
        """Test using cached credentials when they are valid."""
        # Setup - cached credentials
        cached_creds = AuthCredentials(idu="123", login_md5="abc")
        mock_prompt.return_value = (None, None, cached_creds, 'cached')

        # Mock auth service validation
        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service
        mock_auth_service.validate_credentials.return_value = True
        mock_auth_service.establish_session.return_value = True

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is True
        assert cli.credentials == cached_creds
        mock_auth_service.validate_credentials.assert_called_once_with(cached_creds)

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    @patch('src.cli.app.CredentialStorage')
    def test_cached_credentials_expired(self, mock_storage, mock_auth_service_class, mock_prompt):
        """Test that expired cached credentials are cleared and login fails."""
        # Setup - cached credentials that are invalid
        cached_creds = AuthCredentials(idu="123", login_md5="abc")
        mock_prompt.return_value = (None, None, cached_creds, 'cached')

        # Mock auth service validation to return False (invalid)
        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service
        mock_auth_service.validate_credentials.return_value = False

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is False
        mock_auth_service.validate_credentials.assert_called_once_with(cached_creds)
        mock_storage.clear_credentials.assert_called_once()

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    @patch('src.cli.app.CredentialStorage')
    def test_manual_credentials_validated(self, mock_storage, mock_auth_service_class, mock_prompt):
        """Test that manual credentials are validated before saving."""
        # Setup - manual credentials
        manual_creds = AuthCredentials(idu="456", login_md5="def")
        mock_prompt.return_value = (None, None, manual_creds, 'manual-save')

        # Mock auth service validation
        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service
        mock_auth_service.validate_credentials.return_value = True
        mock_auth_service.establish_session.return_value = True

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is True
        mock_auth_service.validate_credentials.assert_called_once_with(manual_creds)
        mock_storage.save_credentials.assert_called_once_with(manual_creds)

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    @patch('src.cli.app.CredentialStorage')
    def test_manual_credentials_invalid(self, mock_storage, mock_auth_service_class, mock_prompt):
        """Test that invalid manual credentials are rejected."""
        # Setup - manual credentials that are invalid
        manual_creds = AuthCredentials(idu="456", login_md5="invalid")
        mock_prompt.return_value = (None, None, manual_creds, 'manual')

        # Mock auth service validation to return False
        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service
        mock_auth_service.validate_credentials.return_value = False

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is False
        mock_auth_service.validate_credentials.assert_called_once_with(manual_creds)
        # Should not save invalid credentials
        mock_storage.save_credentials.assert_not_called()

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    @patch('src.cli.app.CredentialStorage')
    def test_auto_login_saves_without_validation(self, mock_storage, mock_auth_service_class, mock_prompt):
        """Test that auto-login saves credentials without separate validation."""
        # Setup - auto login
        mock_prompt.return_value = ("user@example.com", "password", None, 'auto-save')

        # Mock successful login
        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service

        mock_login_response = Mock()
        mock_login_response.success = True
        mock_login_response.credentials = AuthCredentials(idu="789", login_md5="xyz")
        mock_auth_service.login.return_value = mock_login_response
        mock_auth_service.establish_session.return_value = True

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is True
        # Should save credentials after successful login
        mock_storage.save_credentials.assert_called_once()
        # Should not call validate_credentials (login already validated)
        mock_auth_service.validate_credentials.assert_not_called()
