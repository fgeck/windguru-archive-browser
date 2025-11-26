"""
Authentication-related data models.
"""
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class AuthCredentials:
    """Authentication credentials for Windguru."""
    idu: str
    login_md5: str
    session: Optional[str] = None
    deviceid: Optional[str] = None
    langc: str = 'en-'

    def to_cookies(self) -> Dict[str, str]:
        """Convert credentials to cookies dictionary."""
        cookies = {
            'idu': self.idu,
            'login_md5': self.login_md5,
            'langc': self.langc
        }
        if self.session:
            cookies['session'] = self.session
        if self.deviceid:
            cookies['deviceid'] = self.deviceid
        return cookies

    @classmethod
    def from_cookies(cls, cookies: Dict[str, str]) -> 'AuthCredentials':
        """Create credentials from cookies dictionary."""
        return cls(
            idu=cookies.get('idu', ''),
            login_md5=cookies.get('login_md5', ''),
            session=cookies.get('session'),
            deviceid=cookies.get('deviceid'),
            langc=cookies.get('langc', 'en-')
        )


@dataclass
class LoginResponse:
    """Response from login API."""
    success: bool
    message: str
    credentials: Optional[AuthCredentials] = None
    error: Optional[str] = None
