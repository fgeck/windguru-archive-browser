"""
Tests for credential storage service.
"""
from unittest.mock import patch

from src.models.auth import AuthCredentials
from src.services.credential_storage import CredentialStorage


class TestCredentialStorage:
    """Tests for CredentialStorage service."""

    @patch('src.services.credential_storage.keyring')
    def test_save_username(self, mock_keyring):
        """Test saving username to keyring."""
        CredentialStorage.save_username("test@example.com")

        mock_keyring.set_password.assert_called_once_with(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.USERNAME_KEY,
            "test@example.com"
        )

    @patch('src.services.credential_storage.keyring')
    def test_save_username_fails_silently(self, mock_keyring):
        """Test that save_username fails silently on error."""
        mock_keyring.set_password.side_effect = Exception("Keyring error")

        # Should not raise exception
        CredentialStorage.save_username("test@example.com")

    @patch('src.services.credential_storage.keyring')
    def test_get_username(self, mock_keyring):
        """Test retrieving username from keyring."""
        mock_keyring.get_password.return_value = "test@example.com"

        result = CredentialStorage.get_username()

        assert result == "test@example.com"
        mock_keyring.get_password.assert_called_once_with(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.USERNAME_KEY
        )

    @patch('src.services.credential_storage.keyring')
    def test_get_username_not_found(self, mock_keyring):
        """Test retrieving username when not found."""
        mock_keyring.get_password.return_value = None

        result = CredentialStorage.get_username()

        assert result is None

    @patch('src.services.credential_storage.keyring')
    def test_get_username_fails_silently(self, mock_keyring):
        """Test that get_username fails silently on error."""
        mock_keyring.get_password.side_effect = Exception("Keyring error")

        result = CredentialStorage.get_username()

        assert result is None

    @patch('src.services.credential_storage.keyring')
    def test_save_credentials(self, mock_keyring):
        """Test saving credentials to keyring."""
        credentials = AuthCredentials(idu="123", login_md5="abc123")

        CredentialStorage.save_credentials(credentials)

        assert mock_keyring.set_password.call_count == 2
        mock_keyring.set_password.assert_any_call(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.IDU_KEY,
            "123"
        )
        mock_keyring.set_password.assert_any_call(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.LOGIN_MD5_KEY,
            "abc123"
        )

    @patch('src.services.credential_storage.keyring')
    def test_save_credentials_with_username(self, mock_keyring):
        """Test saving credentials with username to keyring."""
        credentials = AuthCredentials(idu="123", login_md5="abc123")

        CredentialStorage.save_credentials(credentials, username="test@example.com")

        assert mock_keyring.set_password.call_count == 3
        mock_keyring.set_password.assert_any_call(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.USERNAME_KEY,
            "test@example.com"
        )

    @patch('src.services.credential_storage.keyring')
    def test_save_credentials_fails_silently(self, mock_keyring):
        """Test that save_credentials fails silently on error."""
        mock_keyring.set_password.side_effect = Exception("Keyring error")
        credentials = AuthCredentials(idu="123", login_md5="abc123")

        # Should not raise exception
        CredentialStorage.save_credentials(credentials)

    @patch('src.services.credential_storage.keyring')
    def test_get_credentials(self, mock_keyring):
        """Test retrieving credentials from keyring."""
        mock_keyring.get_password.side_effect = lambda service, key: {
            CredentialStorage.IDU_KEY: "123",
            CredentialStorage.LOGIN_MD5_KEY: "abc123"
        }.get(key)

        result = CredentialStorage.get_credentials()

        assert result is not None
        assert result.idu == "123"
        assert result.login_md5 == "abc123"

    @patch('src.services.credential_storage.keyring')
    def test_get_credentials_not_found(self, mock_keyring):
        """Test retrieving credentials when not found."""
        mock_keyring.get_password.return_value = None

        result = CredentialStorage.get_credentials()

        assert result is None

    @patch('src.services.credential_storage.keyring')
    def test_get_credentials_partial(self, mock_keyring):
        """Test retrieving credentials when only partial data exists."""
        mock_keyring.get_password.side_effect = lambda service, key: {
            CredentialStorage.IDU_KEY: "123",
        }.get(key)

        result = CredentialStorage.get_credentials()

        assert result is None

    @patch('src.services.credential_storage.keyring')
    def test_get_credentials_fails_silently(self, mock_keyring):
        """Test that get_credentials fails silently on error."""
        mock_keyring.get_password.side_effect = Exception("Keyring error")

        result = CredentialStorage.get_credentials()

        assert result is None

    @patch('src.services.credential_storage.keyring')
    def test_clear_credentials(self, mock_keyring):
        """Test clearing credentials from keyring."""
        CredentialStorage.clear_credentials()

        assert mock_keyring.delete_password.call_count == 3
        mock_keyring.delete_password.assert_any_call(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.USERNAME_KEY
        )
        mock_keyring.delete_password.assert_any_call(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.IDU_KEY
        )
        mock_keyring.delete_password.assert_any_call(
            CredentialStorage.SERVICE_NAME,
            CredentialStorage.LOGIN_MD5_KEY
        )

    @patch('src.services.credential_storage.keyring')
    def test_clear_credentials_fails_silently(self, mock_keyring):
        """Test that clear_credentials fails silently on errors."""
        mock_keyring.delete_password.side_effect = Exception("Keyring error")

        # Should not raise exception
        CredentialStorage.clear_credentials()

    @patch('src.services.credential_storage.keyring')
    def test_has_saved_credentials_true(self, mock_keyring):
        """Test checking for saved credentials when they exist."""
        mock_keyring.get_password.side_effect = lambda service, key: {
            CredentialStorage.IDU_KEY: "123",
            CredentialStorage.LOGIN_MD5_KEY: "abc123"
        }.get(key)

        result = CredentialStorage.has_saved_credentials()

        assert result is True

    @patch('src.services.credential_storage.keyring')
    def test_has_saved_credentials_false(self, mock_keyring):
        """Test checking for saved credentials when they don't exist."""
        mock_keyring.get_password.return_value = None

        result = CredentialStorage.has_saved_credentials()

        assert result is False
