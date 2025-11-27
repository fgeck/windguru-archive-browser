"""
Spot search service for Windguru API.
"""
import json
from typing import Optional

import requests

from ..config.constants import DEFAULT_HEADERS, WINDGURU_API_URL
from ..models.auth import AuthCredentials
from ..models.spot import Spot, SpotSearchResult


class SpotService:
    """Handles spot search operations."""

    def __init__(self, credentials: AuthCredentials) -> None:
        """
        Initialize spot service.

        Args:
            credentials: Authentication credentials
        """
        self.credentials = credentials
        self.session = requests.Session()

    def search(self, query: str, limit: int = 10) -> SpotSearchResult:
        """
        Search for spots by name.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            SpotSearchResult with found spots
        """
        params = {
            'q': 'autocomplete_ss',
            'type_info': 'true',
            'all': '0',
            'latlon': '1',
            'country': '1',
            'favourite': '1',
            'custom': '1',
            'stations': '1',
            'geonames': '40',
            'spots': '1',
            'priority_sort': '1',
            'query': query,
            '_mha': '58184b7b'
        }

        try:
            response = self.session.get(
                WINDGURU_API_URL,
                params=params,
                cookies=self.credentials.to_cookies(),
                headers=DEFAULT_HEADERS
            )

            if response.status_code != 200:
                return SpotSearchResult(spots=[], query=query, total=0)

            data = json.loads(response.text)
            suggestions = data.get('suggestions', [])

            spots = []
            for suggestion in suggestions[:limit]:
                # Parse spot data
                spot_id = suggestion.get('data')
                spot_name = suggestion.get('value', '')

                # Extract country from name if present (format: "Country - SpotName")
                country = None
                if ' - ' in spot_name:
                    parts = spot_name.split(' - ', 1)
                    country = parts[0]

                spot = Spot(
                    id=int(spot_id) if spot_id else 0,
                    name=spot_name,
                    country=country
                )
                spots.append(spot)

            return SpotSearchResult(
                spots=spots,
                query=query,
                total=len(spots)
            )

        except Exception:
            return SpotSearchResult(spots=[], query=query, total=0)

    def get_spot_by_id(self, spot_id: int) -> Optional[Spot]:
        """
        Get spot information by ID.

        Args:
            spot_id: Spot ID

        Returns:
            Spot if found, None otherwise
        """
        # For now, we don't have a direct API for this
        # Could be implemented if needed
        return Spot(id=spot_id, name=f"Spot {spot_id}")
