"""
Data models and DTOs for Windguru CLI.
"""
from .archive import ArchiveRequest, ArchiveResponse
from .auth import AuthCredentials, LoginResponse
from .spot import Spot, SpotSearchResult
from .weather import DateRange, WeatherData, WeatherModel

__all__ = [
    'AuthCredentials',
    'LoginResponse',
    'Spot',
    'SpotSearchResult',
    'WeatherModel',
    'WeatherData',
    'DateRange',
    'ArchiveRequest',
    'ArchiveResponse',
]
