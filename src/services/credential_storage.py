"""
Secure credential storage service using system keyring.
"""
from typing import Optional

import keyring

from ..models.auth import AuthCredentials


class CredentialStorage:
    """Handles secure storage and retrieval of credentials using system keyring."""

    SERVICE_NAME = "windguru-archive-browser"
    USERNAME_KEY = "username"
    IDU_KEY = "idu"
    LOGIN_MD5_KEY = "login_md5"

    @classmethod
    def save_username(cls, username: str) -> None:
        """
        Save username to keyring.

        Args:
            username: Email/username to save
        """
        try:
            keyring.set_password(cls.SERVICE_NAME, cls.USERNAME_KEY, username)
        except Exception:
            # Silently fail if keyring is not available
            pass

    @classmethod
    def get_username(cls) -> Optional[str]:
        """
        Retrieve saved username from keyring.

        Returns:
            Username if found, None otherwise
        """
        try:
            return keyring.get_password(cls.SERVICE_NAME, cls.USERNAME_KEY)
        except Exception:
            return None

    @classmethod
    def save_credentials(cls, credentials: AuthCredentials, username: Optional[str] = None) -> None:
        """
        Save credentials to keyring.

        Args:
            credentials: AuthCredentials to save
            username: Optional username to associate with credentials
        """
        try:
            keyring.set_password(cls.SERVICE_NAME, cls.IDU_KEY, credentials.idu)
            keyring.set_password(cls.SERVICE_NAME, cls.LOGIN_MD5_KEY, credentials.login_md5)
            if username:
                cls.save_username(username)
        except Exception:
            # Silently fail if keyring is not available
            pass

    @classmethod
    def get_credentials(cls) -> Optional[AuthCredentials]:
        """
        Retrieve saved credentials from keyring.

        Returns:
            AuthCredentials if found, None otherwise
        """
        try:
            idu = keyring.get_password(cls.SERVICE_NAME, cls.IDU_KEY)
            login_md5 = keyring.get_password(cls.SERVICE_NAME, cls.LOGIN_MD5_KEY)

            if idu and login_md5:
                return AuthCredentials(idu=idu, login_md5=login_md5)
            return None
        except Exception:
            return None

    @classmethod
    def clear_credentials(cls) -> None:
        """Clear all saved credentials from keyring."""
        try:
            keyring.delete_password(cls.SERVICE_NAME, cls.USERNAME_KEY)
        except Exception:
            pass

        try:
            keyring.delete_password(cls.SERVICE_NAME, cls.IDU_KEY)
        except Exception:
            pass

        try:
            keyring.delete_password(cls.SERVICE_NAME, cls.LOGIN_MD5_KEY)
        except Exception:
            pass

    @classmethod
    def has_saved_credentials(cls) -> bool:
        """
        Check if credentials are saved in keyring.

        Returns:
            True if credentials exist, False otherwise
        """
        return cls.get_credentials() is not None
