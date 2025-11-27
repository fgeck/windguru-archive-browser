"""
Archive data fetching and parsing service.
"""
import re
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

from ..config.constants import (
    DEFAULT_HEADERS,
    MIN_USE_HR,
    WINDGURU_ARCHIVE_URL,
    WINDGURU_BASE_URL,
)
from ..models.archive import ArchiveRequest, ArchiveResponse
from ..models.auth import AuthCredentials
from ..models.weather import WeatherData


class ArchiveService:
    """Handles fetching and parsing of archive data."""

    def __init__(self, credentials: AuthCredentials) -> None:
        """
        Initialize archive service.

        Args:
            credentials: Authentication credentials
        """
        self.credentials = credentials
        self.session = requests.Session()

    def fetch(self, request: ArchiveRequest) -> ArchiveResponse:
        """
        Fetch archive data from Windguru.

        Args:
            request: Archive request parameters

        Returns:
            ArchiveResponse with HTML content
        """
        try:
            # Establish session
            self.session.get(
                f'{WINDGURU_BASE_URL}/archive.php',
                cookies=self.credentials.to_cookies()
            )

            # Build form data
            data = [
                ('date_from', request.date_range.start.strftime('%Y-%m-%d')),
                ('date_to', request.date_range.end.strftime('%Y-%m-%d')),
                ('step', str(request.step_hours)),
                ('min_use_hr', str(MIN_USE_HR)),
                ('id_spot', str(request.spot_id)),
                ('id_model', str(request.model_id)),
                ('id_stats_type', '')
            ]

            # Add variables
            for var in request.variables:
                data.append(('arch_params[]', var))

            response = self.session.post(
                WINDGURU_ARCHIVE_URL,
                data=data,
                cookies=self.credentials.to_cookies(),
                headers=DEFAULT_HEADERS
            )

            if response.status_code != 200:
                return ArchiveResponse(
                    html_content='',
                    success=False,
                    error=f"HTTP {response.status_code}"
                )

            return ArchiveResponse(
                html_content=response.text,
                success=True
            )

        except Exception as e:
            return ArchiveResponse(
                html_content='',
                success=False,
                error=str(e)
            )

    def parse(self, response: ArchiveResponse) -> pd.DataFrame:
        """
        Parse HTML archive data into DataFrame.

        Args:
            response: Archive response with HTML content

        Returns:
            pandas.DataFrame with parsed data
        """
        if not response.has_data:
            return pd.DataFrame()

        soup = BeautifulSoup(response.html_content, 'html.parser')

        # Find the main forecast table
        table = soup.find('table', class_='daily-archive')
        if not table:
            raise Exception("Could not find archive data table in HTML")

        # Parse header to find which variables are present and their column spans
        header_row = table.find_all('tr')[0]
        variable_headers = []
        for td in header_row.find_all('td'):
            colspan_attr = td.get('colspan')
            if colspan_attr:
                colspan = int(str(colspan_attr))
                text = td.get_text(strip=True)
                variable_headers.append((text, colspan))

        # Parse data rows
        data_rows = []
        for row in table.find_all('tr')[2:]:  # Skip first 2 header rows
            cells = row.find_all('td')
            if not cells:
                continue

            # First cell is the date
            date_str = cells[0].get_text(strip=True)
            try:
                date = datetime.strptime(date_str, '%d.%m.%Y').date()
            except ValueError:
                continue

            # Determine variable boundaries based on colspan
            col_idx = 1  # Start after date column

            # Extract data for each time point
            num_time_points = variable_headers[0][1] if variable_headers else 12

            for time_idx in range(num_time_points):
                row_data = {'date': date, 'hour': time_idx * 2}

                # Extract values for each variable at this time point
                current_col = col_idx + time_idx
                for var_name, colspan in variable_headers:
                    cell = cells[current_col] if current_col < len(cells) else None

                    if cell:
                        # Check if it's wind direction (SVG arrow)
                        svg = cell.find('svg')
                        if svg:
                            g = svg.find('g')
                            transform_attr = g.get('transform') if g else None
                            if transform_attr:
                                match = re.search(r'rotate\((\d+)', str(transform_attr))
                                if match:
                                    wind_dir = int(match.group(1)) % 360
                                    row_data['wind_dir'] = wind_dir
                        else:
                            # Extract numeric value
                            text = cell.get_text(strip=True)
                            try:
                                value = float(text)
                                if 'Wind speed' in var_name:
                                    row_data['wind_speed'] = value
                                elif 'Temperature' in var_name:
                                    row_data['temperature'] = value
                                elif 'Wind gusts' in var_name:
                                    row_data['wind_gust'] = value
                            except ValueError:
                                pass

                    # Move to next variable's columns
                    current_col += colspan

                data_rows.append(row_data)

        # Convert to DataFrame
        df = pd.DataFrame(data_rows)

        # Create datetime column
        if 'date' in df.columns and 'hour' in df.columns:
            df['datetime'] = pd.to_datetime(
                df['date'].astype(str) + ' ' + df['hour'].astype(str) + ':00:00'
            )

        return df

    def get_weather_data(self, request: ArchiveRequest,
                         spot_name: Optional[str] = None,
                         model_name: Optional[str] = None) -> WeatherData:
        """
        Fetch and parse weather data in one call.

        Args:
            request: Archive request parameters
            spot_name: Optional spot name for metadata
            model_name: Optional model name for metadata

        Returns:
            WeatherData with parsed DataFrame
        """
        response = self.fetch(request)
        if not response.success:
            raise Exception(f"Failed to fetch archive data: {response.error}")

        df = self.parse(response)

        return WeatherData(
            spot_id=request.spot_id,
            model_id=request.model_id,
            date_range=request.date_range,
            dataframe=df,
            spot_name=spot_name,
            model_name=model_name
        )
