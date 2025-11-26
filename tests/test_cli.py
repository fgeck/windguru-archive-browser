"""
Tests for CLI components.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.cli.formatter import CLIFormatter
from src.cli.app import WindguruCLI
from src.config.settings import Settings
from src.models.auth import AuthCredentials


class TestCLIFormatter:
    """Tests for CLIFormatter."""

    def test_header(self):
        """Test creating header."""
        formatter = CLIFormatter()
        result = formatter.header("TEST", width=20)

        assert "TEST" in result
        assert "=" * 20 in result

    def test_subheader(self):
        """Test creating subheader."""
        formatter = CLIFormatter()
        result = formatter.subheader("TEST", width=20)

        assert "TEST" in result
        assert "-" * 20 in result

    def test_success(self):
        """Test success message."""
        formatter = CLIFormatter()
        result = formatter.success("Operation completed")

        assert "✅" in result
        assert "Operation completed" in result

    def test_error(self):
        """Test error message."""
        formatter = CLIFormatter()
        result = formatter.error("Something went wrong")

        assert "❌" in result
        assert "Something went wrong" in result

    def test_info(self):
        """Test info message."""
        formatter = CLIFormatter()
        result = formatter.info("Information")

        assert "ℹ️" in result
        assert "Information" in result

    def test_working(self):
        """Test working message."""
        formatter = CLIFormatter()
        result = formatter.working("Processing...")

        assert "🔄" in result
        assert "Processing..." in result

    def test_section_break(self):
        """Test section break."""
        formatter = CLIFormatter()
        result = formatter.section_break(width=30)

        assert "=" * 30 in result


class TestWindguruCLI:
    """Tests for WindguruCLI."""

    def test_init_default_settings(self):
        """Test initializing CLI with default settings."""
        cli = WindguruCLI()

        assert cli.settings is not None
        assert cli.fmt is not None
        assert cli.credentials is None
        assert cli.auth_service is None

    def test_init_custom_settings(self):
        """Test initializing CLI with custom settings."""
        settings = Settings(verbose=True)
        cli = WindguruCLI(settings)

        assert cli.settings.verbose is True

    def test_print_banner(self, capsys):
        """Test printing banner."""
        cli = WindguruCLI()
        cli.print_banner()

        captured = capsys.readouterr()
        assert "WINDGURU DATA ANALYZER" in captured.out
        assert "🌊" in captured.out

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    def test_authenticate_auto_success(self, mock_auth_service_class, mock_prompt):
        """Test successful auto authentication."""
        # Setup mocks
        mock_prompt.return_value = (
            "test@example.com",
            "password",
            None,
            "auto"
        )

        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service

        mock_login_response = Mock()
        mock_login_response.success = True
        mock_login_response.credentials = AuthCredentials(
            idu="123",
            login_md5="abc"
        )
        mock_auth_service.login.return_value = mock_login_response
        mock_auth_service.establish_session.return_value = True

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is True
        assert cli.credentials is not None
        assert cli.credentials.idu == "123"

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    def test_authenticate_auto_failure(self, mock_auth_service_class, mock_prompt):
        """Test failed auto authentication."""
        # Setup mocks
        mock_prompt.return_value = (
            "test@example.com",
            "wrong_password",
            None,
            "auto"
        )

        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service

        mock_login_response = Mock()
        mock_login_response.success = False
        mock_login_response.error = "Invalid credentials"
        mock_auth_service.login.return_value = mock_login_response

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is False
        assert cli.credentials is None

    @patch('src.cli.app.CredentialsPrompt.prompt')
    @patch('src.cli.app.AuthService')
    def test_authenticate_manual(self, mock_auth_service_class, mock_prompt):
        """Test manual authentication."""
        # Setup mocks
        credentials = AuthCredentials(idu="123", login_md5="abc")
        mock_prompt.return_value = (
            None,
            None,
            credentials,
            "manual"
        )

        mock_auth_service = MagicMock()
        mock_auth_service_class.return_value = mock_auth_service
        mock_auth_service.establish_session.return_value = True

        # Test
        cli = WindguruCLI()
        result = cli.authenticate()

        assert result is True
        assert cli.credentials == credentials

    @patch('src.cli.app.SpotPrompt.prompt_search')
    @patch('src.cli.app.SpotPrompt.display_results')
    def test_select_spot_success(self, mock_display, mock_search):
        """Test successful spot selection."""
        from src.models.spot import Spot, SpotSearchResult

        # Setup mocks
        mock_search.return_value = "test beach"

        mock_spot = Spot(id=123, name="Test Beach", country="Greece")
        mock_display.return_value = mock_spot

        # Mock spot service
        mock_spot_service = MagicMock()
        mock_spot_service.search.return_value = SpotSearchResult(
            spots=[mock_spot],
            query="test beach",
            total=1
        )

        # Test
        cli = WindguruCLI()
        cli.spot_service = mock_spot_service

        result = cli.select_spot()

        assert result == mock_spot
        mock_search.assert_called_once()
        mock_display.assert_called_once()
