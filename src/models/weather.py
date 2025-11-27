"""
Weather-related data models.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

import pandas as pd


@dataclass
class WeatherModel:
    """Represents a weather forecast model."""
    id: int
    name: str
    resolution: Optional[str] = None
    coverage: Optional[str] = None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        return self.name


@dataclass
class DateRange:
    """Represents a date range."""
    start: date
    end: date

    def __post_init__(self) -> None:
        """Validate date range."""
        if self.end < self.start:
            raise ValueError("End date must be after start date")

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.start} to {self.end}"

    @property
    def days(self) -> int:
        """Calculate number of days in range."""
        return (self.end - self.start).days + 1


@dataclass
class WeatherData:
    """Container for parsed weather data."""
    spot_id: int
    model_id: int
    date_range: DateRange
    dataframe: pd.DataFrame
    spot_name: Optional[str] = None
    model_name: Optional[str] = None

    @property
    def record_count(self) -> int:
        """Return number of records."""
        return len(self.dataframe)

    @property
    def has_wind_speed(self) -> bool:
        """Check if wind speed data is present."""
        return 'wind_speed' in self.dataframe.columns

    @property
    def has_wind_direction(self) -> bool:
        """Check if wind direction data is present."""
        return 'wind_dir' in self.dataframe.columns

    @property
    def has_temperature(self) -> bool:
        """Check if temperature data is present."""
        return 'temperature' in self.dataframe.columns

    def get_summary_stats(self) -> dict:
        """Calculate summary statistics."""
        stats = {}

        if self.has_wind_speed:
            wind_speed = self.dataframe['wind_speed'].dropna()
            stats['wind_speed'] = {
                'mean': wind_speed.mean(),
                'median': wind_speed.median(),
                'min': wind_speed.min(),
                'max': wind_speed.max(),
                'std': wind_speed.std()
            }

            # Wind speed ranges
            total = len(wind_speed)
            if total > 0:
                stats['wind_ranges'] = {
                    '0-10_knots': len(wind_speed[wind_speed < 10]) / total * 100,
                    '10-20_knots': len(wind_speed[(wind_speed >= 10) & (wind_speed < 20)]) / total * 100,
                    '15-25_knots': len(wind_speed[(wind_speed >= 15) & (wind_speed < 25)]) / total * 100,
                    '20-30_knots': len(wind_speed[(wind_speed >= 20) & (wind_speed < 30)]) / total * 100,
                    '30+_knots': len(wind_speed[wind_speed >= 30]) / total * 100,
                }

        if self.has_temperature:
            temp = self.dataframe['temperature'].dropna()
            stats['temperature'] = {
                'mean': temp.mean(),
                'median': temp.median(),
                'min': temp.min(),
                'max': temp.max(),
                'std': temp.std()
            }

        return stats
