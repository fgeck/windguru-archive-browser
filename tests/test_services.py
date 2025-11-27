"""
Tests for service classes.
"""
from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

from src.models.archive import ArchiveRequest, ArchiveResponse
from src.models.auth import AuthCredentials
from src.models.weather import DateRange, WeatherData
from src.services.archive_service import ArchiveService
from src.services.auth_service import AuthService
from src.services.spot_service import SpotService
from src.services.visualization_service import VisualizationService


class TestAuthService:
    """Tests for AuthService."""

    def test_init(self):
        """Test initializing auth service."""
        service = AuthService()
        assert service.session is not None

    @patch('src.services.auth_service.requests.Session')
    def test_login_success(self, mock_session_class):
        """Test successful login."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'return': 'OK',
            'data': {
                'id_user': 123,
                'login_md5': 'abc123'
            }
        }
        mock_session.get.return_value = mock_response

        # Test
        service = AuthService()
        result = service.login("test@example.com", "password")

        assert result.success is True
        assert result.credentials.idu == "123"
        assert result.credentials.login_md5 == "abc123"

    @patch('src.services.auth_service.requests.Session')
    def test_login_failure(self, mock_session_class):
        """Test failed login."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'return': 'ERROR',
            'message': 'Invalid credentials'
        }
        mock_session.get.return_value = mock_response

        # Test
        service = AuthService()
        result = service.login("test@example.com", "wrong_password")

        assert result.success is False
        assert "Invalid credentials" in result.error

    @patch('src.services.auth_service.requests.Session')
    def test_establish_session(self, mock_session_class):
        """Test establishing session."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        # Test
        service = AuthService()
        credentials = AuthCredentials(idu="123", login_md5="abc")
        result = service.establish_session(credentials)

        assert result is True
        mock_session.get.assert_called_once()


class TestSpotService:
    """Tests for SpotService."""

    def test_init(self):
        """Test initializing spot service."""
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = SpotService(credentials)

        assert service.credentials == credentials
        assert service.session is not None

    @patch('src.services.spot_service.requests.Session')
    def test_search_success(self, mock_session_class):
        """Test successful spot search."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        {
            "suggestions": [
                {"data": "123", "value": "Greece - Test Beach"},
                {"data": "456", "value": "Spain - Another Beach"}
            ]
        }
        '''
        mock_session.get.return_value = mock_response

        # Test
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = SpotService(credentials)
        result = service.search("beach")

        assert len(result.spots) == 2
        assert result.spots[0].id == 123
        assert result.spots[0].name == "Greece - Test Beach"
        assert result.spots[0].country == "Greece"

    @patch('src.services.spot_service.requests.Session')
    def test_search_no_results(self, mock_session_class):
        """Test spot search with no results."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"suggestions": []}'
        mock_session.get.return_value = mock_response

        # Test
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = SpotService(credentials)
        result = service.search("nonexistent")

        assert len(result.spots) == 0
        assert result.total == 0

    def test_get_spot_by_id(self):
        """Test getting spot by ID."""
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = SpotService(credentials)
        spot = service.get_spot_by_id(123)

        assert spot.id == 123
        assert "Spot 123" in spot.name


class TestArchiveService:
    """Tests for ArchiveService."""

    def test_init(self):
        """Test initializing archive service."""
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = ArchiveService(credentials)

        assert service.credentials == credentials
        assert service.session is not None

    @patch('src.services.archive_service.requests.Session')
    def test_fetch_success(self, mock_session_class):
        """Test successful archive fetch."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.text = "<html>archive data</html>"

        mock_session.get.return_value = mock_get_response
        mock_session.post.return_value = mock_post_response

        # Test
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = ArchiveService(credentials)

        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        request = ArchiveRequest(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            variables=['WINDSPD', 'WINDDIR']
        )

        result = service.fetch(request)

        assert result.success is True
        assert "archive data" in result.html_content

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = ArchiveService(credentials)

        response = ArchiveResponse(html_content="", success=False)
        result = service.parse(response)

        assert result.empty

    @patch('src.services.archive_service.requests.Session')
    def test_get_weather_data(self, mock_session_class):
        """Test getting weather data."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock HTML with simple table structure
        mock_html = """
        <table class="daily-archive">
            <tr><td colspan="12">Wind speed</td></tr>
            <tr><td>Header</td></tr>
            <tr>
                <td>01.01.2024</td>
                <td>10</td><td>12</td><td>15</td>
            </tr>
        </table>
        """

        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.text = mock_html

        mock_session.get.return_value = mock_get_response
        mock_session.post.return_value = mock_post_response

        # Test
        credentials = AuthCredentials(idu="123", login_md5="abc")
        service = ArchiveService(credentials)

        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        request = ArchiveRequest(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            variables=['WINDSPD']
        )

        result = service.get_weather_data(request, spot_name="Test Beach")

        assert isinstance(result, WeatherData)
        assert result.spot_name == "Test Beach"
        assert result.spot_id == 123


class TestVisualizationService:
    """Tests for VisualizationService."""

    def test_init(self, tmp_path):
        """Test initializing visualization service."""
        output_dir = tmp_path / "output"
        service = VisualizationService(output_dir)

        assert service.output_dir == output_dir
        assert output_dir.exists()

    def test_create_dashboard(self, tmp_path):
        """Test creating dashboard."""
        output_dir = tmp_path / "output"
        service = VisualizationService(output_dir)

        # Create test data
        df = pd.DataFrame({
            'datetime': pd.date_range('2024-01-01', periods=10, freq='h'),
            'wind_speed': [10.0, 12.0, 15.0, 18.0, 20.0, 22.0, 18.0, 15.0, 12.0, 10.0],
            'wind_dir': [180] * 10,
            'temperature': [20.0, 21.0, 22.0, 23.0, 24.0, 23.0, 22.0, 21.0, 20.0, 19.0]
        })

        date_range = DateRange(date(2024, 1, 1), date(2024, 1, 31))
        weather_data = WeatherData(
            spot_id=123,
            model_id=3,
            date_range=date_range,
            dataframe=df,
            spot_name="Test Beach"
        )

        # Create dashboard
        result = service.create_dashboard(weather_data)

        assert result.exists()
        assert result.suffix == ".html"
        assert "Test_Beach" in result.name

        # Check that HTML file has content
        content = result.read_text()
        assert len(content) > 0
        assert "plotly" in content.lower()
