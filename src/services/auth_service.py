"""
Authentication service for Windguru API.
"""

import requests

from ..config.constants import DEFAULT_HEADERS, WINDGURU_API_URL, WINDGURU_BASE_URL
from ..models.auth import AuthCredentials, LoginResponse


class AuthService:
    """Handles authentication with Windguru."""

    def __init__(self) -> None:
        """Initialize authentication service."""
        self.session = requests.Session()

    def login(self, email: str, password: str) -> LoginResponse:
        """
        Login to Windguru using email and password.

        Args:
            email: User email/username
            password: User password

        Returns:
            LoginResponse with credentials if successful
        """
        try:
            # Visit main page to establish session
            self.session.get(WINDGURU_BASE_URL)

            # Call login API
            params = {
                'q': 'wg_login',
                'username': email,
                'password': password
            }

            response = self.session.get(
                WINDGURU_API_URL,
                params=params,
                headers=DEFAULT_HEADERS
            )

            if response.status_code != 200:
                return LoginResponse(
                    success=False,
                    message=f"HTTP {response.status_code}",
                    error=f"Login failed with HTTP {response.status_code}"
                )

            result = response.json()

            if result.get('return') != 'OK':
                error_msg = result.get('message', 'Login failed')
                return LoginResponse(
                    success=False,
                    message=error_msg,
                    error=error_msg
                )

            # Extract credentials
            data = result.get('data', {})
            credentials = AuthCredentials(
                idu=str(data.get('id_user')),
                login_md5=data.get('login_md5'),
                langc='en-'
            )

            # Add any session cookies
            for cookie in self.session.cookies:
                if cookie.name == 'session':
                    credentials.session = cookie.value
                elif cookie.name == 'deviceid':
                    credentials.deviceid = cookie.value

            return LoginResponse(
                success=True,
                message="Login successful",
                credentials=credentials
            )

        except requests.RequestException as e:
            return LoginResponse(
                success=False,
                message="Connection error",
                error=str(e)
            )
        except Exception as e:
            return LoginResponse(
                success=False,
                message="Unexpected error",
                error=str(e)
            )

    def establish_session(self, credentials: AuthCredentials) -> bool:
        """
        Establish session with existing credentials.

        Args:
            credentials: Authentication credentials

        Returns:
            True if session established successfully
        """
        try:
            response = self.session.get(
                f'{WINDGURU_BASE_URL}/archive.php',
                cookies=credentials.to_cookies()
            )
            return response.status_code == 200
        except Exception:
            return False

    def validate_credentials(self, credentials: AuthCredentials) -> bool:
        """
        Validate that credentials are still valid.

        Args:
            credentials: Authentication credentials to validate

        Returns:
            True if credentials are valid
        """
        return self.establish_session(credentials)
