"""
Data models and DTOs for Windguru CLI.
"""
from .auth import AuthCredentials, LoginResponse
from .spot import Spot, SpotSearchResult
from .weather import WeatherModel, WeatherData, DateRange
from .archive import ArchiveRequest, ArchiveResponse

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
