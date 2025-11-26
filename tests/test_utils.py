"""
Tests for utility functions.
"""
import pytest
from datetime import date, datetime
import pandas as pd

from src.utils.date_utils import (
    parse_date_input,
    get_last_day_of_month,
    parse_date_range_input
)
from src.utils.file_utils import generate_safe_filename, ensure_dir
from src.utils.stats_utils import format_stats, print_weather_stats
from src.models.weather import WeatherData, DateRange


class TestDateUtils:
    """Tests for date utility functions."""

    def test_parse_date_input_yyyy_mm(self):
        """Test parsing YYYY-MM format."""
        result = parse_date_input("2024-05")
        assert result == date(2024, 5, 1)

    def test_parse_date_input_yyyy_mm_dd(self):
        """Test parsing YYYY-MM-DD format."""
        result = parse_date_input("2024-05-15")
        assert result == date(2024, 5, 15)

    def test_parse_date_input_invalid(self):
        """Test parsing invalid date format."""
        with pytest.raises(ValueError):
            parse_date_input("2024/05/15")

    def test_get_last_day_of_month_regular(self):
        """Test getting last day of a regular month."""
        result = get_last_day_of_month(2024, 1)
        assert result == date(2024, 1, 31)

    def test_get_last_day_of_month_february_leap(self):
        """Test getting last day of February in leap year."""
        result = get_last_day_of_month(2024, 2)
        assert result == date(2024, 2, 29)

    def test_get_last_day_of_month_february_non_leap(self):
        """Test getting last day of February in non-leap year."""
        result = get_last_day_of_month(2023, 2)
        assert result == date(2023, 2, 28)

    def test_get_last_day_of_month_december(self):
        """Test getting last day of December."""
        result = get_last_day_of_month(2024, 12)
        assert result == date(2024, 12, 31)

    def test_parse_date_range_input_full_dates(self):
        """Test parsing date range with full dates."""
        result = parse_date_range_input("2024-01-01", "2024-01-31")
        assert result.start == date(2024, 1, 1)
        assert result.end == date(2024, 1, 31)

    def test_parse_date_range_input_months(self):
        """Test parsing date range with month format."""
        result = parse_date_range_input("2024-01", "2024-02")
        assert result.start == date(2024, 1, 1)
        assert result.end == date(2024, 2, 29)  # 2024 is leap year

    def test_parse_date_range_input_mixed(self):
        """Test parsing date range with mixed formats."""
        result = parse_date_range_input("2024-01-15", "2024-02")
        assert result.start == date(2024, 1, 15)
        assert result.end == date(2024, 2, 29)

    def test_parse_date_range_input_invalid_order(self):
        """Test that invalid date order raises error."""
        with pytest.raises(ValueError):
            parse_date_range_input("2024-02-01", "2024-01-01")


class TestFileUtils:
    """Tests for file utility functions."""

    def test_generate_safe_filename_basic(self):
        """Test generating safe filename."""
        result = generate_safe_filename("Test Beach")
        assert result.startswith("Test_Beach_")
        assert result.endswith(".html")

    def test_generate_safe_filename_with_special_chars(self):
        """Test generating safe filename with special characters."""
        result = generate_safe_filename("Test/Beach@123!")
        assert result.startswith("TestBeach123_")
        assert "/" not in result
        assert "@" not in result

    def test_generate_safe_filename_with_suffix(self):
        """Test generating safe filename with suffix."""
        result = generate_safe_filename("Test Beach", suffix="dashboard")
        assert "dashboard" in result

    def test_generate_safe_filename_custom_extension(self):
        """Test generating safe filename with custom extension."""
        result = generate_safe_filename("Test Beach", extension="pdf")
        assert result.endswith(".pdf")

    def test_ensure_dir(self, tmp_path):
        """Test ensuring directory exists."""
        test_dir = tmp_path / "test" / "nested" / "dir"
        result = ensure_dir(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir


class TestStatsUtils:
    """Tests for statistics utility functions."""

    def test_format_stats_wind_speed(self):
        """Test formatting wind speed stats."""
        stats = {
            'wind_speed': {
                'mean': 15.5,
                'median': 14.0,
                'min': 5.0,
                'max': 30.0,
                'std': 5.2
            }
        }

        result = format_stats(stats)

        assert "WIND SPEED (knots)" in result
        assert "Mean:    15.5" in result
        assert "Median:  14.0" in result
        assert "Min:     5.0" in result
        assert "Max:     30.0" in result

    def test_format_stats_temperature(self):
        """Test formatting temperature stats."""
        stats = {
            'temperature': {
                'mean': 22.5,
                'median': 23.0,
                'min': 15.0,
                'max': 30.0,
                'std': 3.5
            }
        }

        result = format_stats(stats)

        assert "TEMPERATURE (°C)" in result
        assert "Mean:    22.5" in result

    def test_format_stats_wind_ranges(self):
        """Test formatting wind range stats."""
        stats = {
            'wind_ranges': {
                '10-20_knots': 45.5,
                '15-25_knots': 30.2,
                '20-30_knots': 15.0
            }
        }

        result = format_stats(stats)

        assert "FAVORABLE CONDITIONS" in result
        assert "10-20 knots: 45.5%" in result

    def test_print_weather_stats(self, capsys):
        """Test printing weather stats."""
        df = pd.DataFrame({
            'wind_speed': [10.0, 15.0, 20.0],
            'temperature': [20.0, 22.0, 24.0]
        })

        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        weather_data = WeatherData(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            dataframe=df,
            spot_name="Test Beach"
        )

        print_weather_stats(weather_data)
        captured = capsys.readouterr()

        assert "Test Beach" in captured.out
        assert "2024-01-01 to 2024-01-31" in captured.out
        assert "Total Records: 3" in captured.out
