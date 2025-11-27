"""
Configuration for Windguru CLI.
"""
from .constants import (
    DEFAULT_HEADERS,
    OUTPUT_DIR,
    WEATHER_MODELS,
    WINDGURU_API_URL,
    WINDGURU_BASE_URL,
)
from .settings import Settings

__all__ = [
    'WINDGURU_BASE_URL',
    'WINDGURU_API_URL',
    'WEATHER_MODELS',
    'DEFAULT_HEADERS',
    'OUTPUT_DIR',
    'Settings',
]
