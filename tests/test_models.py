"""
Tests for data models.
"""
from datetime import date

import pandas as pd
import pytest

from src.models.archive import ArchiveRequest, ArchiveResponse
from src.models.auth import AuthCredentials, LoginResponse
from src.models.spot import Spot, SpotSearchResult
from src.models.weather import DateRange, WeatherData, WeatherModel


class TestAuthCredentials:
    """Tests for AuthCredentials model."""

    def test_to_cookies(self):
        """Test converting credentials to cookies."""
        creds = AuthCredentials(idu="123", login_md5="abc", session="xyz")
        cookies = creds.to_cookies()

        assert cookies["idu"] == "123"
        assert cookies["login_md5"] == "abc"
        assert cookies["session"] == "xyz"
        assert cookies["langc"] == "en-"

    def test_from_cookies(self):
        """Test creating credentials from cookies."""
        cookies = {
            "idu": "456",
            "login_md5": "def",
            "session": "uvw",
            "langc": "de-"
        }
        creds = AuthCredentials.from_cookies(cookies)

        assert creds.idu == "456"
        assert creds.login_md5 == "def"
        assert creds.session == "uvw"
        assert creds.langc == "de-"


class TestLoginResponse:
    """Tests for LoginResponse model."""

    def test_successful_login(self):
        """Test successful login response."""
        creds = AuthCredentials(idu="123", login_md5="abc")
        response = LoginResponse(
            success=True,
            message="Login successful",
            credentials=creds
        )

        assert response.success is True
        assert response.message == "Login successful"
        assert response.credentials == creds
        assert response.error is None

    def test_failed_login(self):
        """Test failed login response."""
        response = LoginResponse(
            success=False,
            message="Login failed",
            error="Invalid credentials"
        )

        assert response.success is False
        assert response.error == "Invalid credentials"
        assert response.credentials is None


class TestSpot:
    """Tests for Spot model."""

    def test_spot_creation(self):
        """Test creating a spot."""
        spot = Spot(id=123, name="Test Beach", country="Greece")

        assert spot.id == 123
        assert spot.name == "Test Beach"
        assert spot.country == "Greece"

    def test_spot_string_with_country(self):
        """Test string representation with country."""
        spot = Spot(id=123, name="Test Beach", country="Greece")
        assert str(spot) == "Greece - Test Beach (ID: 123)"

    def test_spot_string_without_country(self):
        """Test string representation without country."""
        spot = Spot(id=123, name="Test Beach")
        assert str(spot) == "Test Beach (ID: 123)"


class TestSpotSearchResult:
    """Tests for SpotSearchResult model."""

    def test_search_result(self):
        """Test spot search result."""
        spots = [
            Spot(id=1, name="Beach 1"),
            Spot(id=2, name="Beach 2")
        ]
        result = SpotSearchResult(spots=spots, query="beach", total=2)

        assert len(result) == 2
        assert result.query == "beach"
        assert result.total == 2
        assert list(result) == spots


class TestWeatherModel:
    """Tests for WeatherModel."""

    def test_weather_model_creation(self):
        """Test creating a weather model."""
        model = WeatherModel(
            id=3,
            name="GFS 13km",
            resolution="13km",
            coverage="World"
        )

        assert model.id == 3
        assert model.name == "GFS 13km"
        assert str(model) == "GFS 13km"


class TestDateRange:
    """Tests for DateRange model."""

    def test_valid_date_range(self):
        """Test creating a valid date range."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        date_range = DateRange(start=start, end=end)

        assert date_range.start == start
        assert date_range.end == end
        assert date_range.days == 31

    def test_invalid_date_range(self):
        """Test that invalid date range raises error."""
        with pytest.raises(ValueError):
            DateRange(start=date(2024, 2, 1), end=date(2024, 1, 1))

    def test_date_range_string(self):
        """Test date range string representation."""
        date_range = DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 31)
        )
        assert str(date_range) == "2024-01-01 to 2024-01-31"


class TestWeatherData:
    """Tests for WeatherData model."""

    def test_weather_data_properties(self):
        """Test weather data properties."""
        df = pd.DataFrame({
            'datetime': pd.date_range('2024-01-01', periods=10, freq='h'),
            'wind_speed': [10.0] * 10,
            'wind_dir': [180] * 10,
            'temperature': [20.0] * 10
        })

        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        weather_data = WeatherData(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            dataframe=df,
            spot_name="Test Beach"
        )

        assert weather_data.record_count == 10
        assert weather_data.has_wind_speed is True
        assert weather_data.has_wind_direction is True
        assert weather_data.has_temperature is True

    def test_summary_stats(self):
        """Test calculating summary statistics."""
        df = pd.DataFrame({
            'wind_speed': [10.0, 15.0, 20.0, 25.0, 30.0],
            'temperature': [15.0, 20.0, 25.0, 30.0, 35.0]
        })

        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        weather_data = WeatherData(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            dataframe=df
        )

        stats = weather_data.get_summary_stats()

        assert 'wind_speed' in stats
        assert stats['wind_speed']['mean'] == 20.0
        assert stats['wind_speed']['min'] == 10.0
        assert stats['wind_speed']['max'] == 30.0
        assert 'temperature' in stats
        assert stats['temperature']['mean'] == 25.0


class TestArchiveRequest:
    """Tests for ArchiveRequest model."""

    def test_create_with_wind_and_temp(self):
        """Test creating archive request with wind and temperature."""
        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        request = ArchiveRequest.create(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            include_wind=True,
            include_temp=True
        )

        assert request.spot_id == 123
        assert request.model_id == 3
        assert 'WINDSPD' in request.variables
        assert 'WINDDIR' in request.variables
        assert 'TMP' in request.variables

    def test_create_wind_only(self):
        """Test creating archive request with wind only."""
        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        request = ArchiveRequest.create(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            include_wind=True,
            include_temp=False
        )

        assert 'WINDSPD' in request.variables
        assert 'WINDDIR' in request.variables
        assert 'TMP' not in request.variables


class TestArchiveResponse:
    """Tests for ArchiveResponse model."""

    def test_successful_response(self):
        """Test successful archive response."""
        response = ArchiveResponse(
            html_content="<html>data</html>",
            success=True
        )

        assert response.success is True
        assert response.has_data is True
        assert response.error is None

    def test_failed_response(self):
        """Test failed archive response."""
        response = ArchiveResponse(
            html_content="",
            success=False,
            error="Connection error"
        )

        assert response.success is False
        assert response.has_data is False
        assert response.error == "Connection error"
