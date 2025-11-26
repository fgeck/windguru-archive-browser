"""
Configuration for Windguru CLI.
"""
from .constants import (
    WINDGURU_BASE_URL,
    WINDGURU_API_URL,
    WEATHER_MODELS,
    DEFAULT_HEADERS,
    OUTPUT_DIR
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
