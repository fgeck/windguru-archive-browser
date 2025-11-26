"""
Constants used throughout the application.
"""
from pathlib import Path

# API URLs
WINDGURU_BASE_URL = 'https://www.windguru.cz'
WINDGURU_API_URL = f'{WINDGURU_BASE_URL}/int/iapi.php'
WINDGURU_ARCHIVE_URL = f'{WINDGURU_BASE_URL}/ajax/ajax_archive.php'

# HTTP Headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0',
    'Referer': WINDGURU_BASE_URL,
}

# Weather Models
WEATHER_MODELS = [
    {'id': 3, 'name': 'GFS 13 km (World)', 'resolution': '13km', 'coverage': 'World'},
    {'id': 117, 'name': 'IFS-HRES 9 km (World)', 'resolution': '9km', 'coverage': 'World'},
    {'id': 21, 'name': 'WRF 9 km (Europe)', 'resolution': '9km', 'coverage': 'Europe'},
    {'id': 43, 'name': 'ICON 7 km (Europe)', 'resolution': '7km', 'coverage': 'Europe'},
    {'id': 45, 'name': 'ICON 13 km (World)', 'resolution': '13km', 'coverage': 'World'},
]

# Output
OUTPUT_DIR = Path('output')

# Archive parameters
DEFAULT_ARCHIVE_VARIABLES = ['WINDSPD', 'WINDDIR', 'TMP']
DEFAULT_STEP_HOURS = 2
MIN_USE_HR = 6

# Visualization
WIND_SPEED_ZONES = [
    {'min': 0, 'max': 10, 'color': 'gray', 'label': 'Light'},
    {'min': 10, 'max': 20, 'color': 'green', 'label': 'Moderate'},
    {'min': 20, 'max': 30, 'color': 'yellow', 'label': 'Strong'},
    {'min': 30, 'max': 100, 'color': 'red', 'label': 'Very Strong'},
]
