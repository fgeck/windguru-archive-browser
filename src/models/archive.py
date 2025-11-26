"""
Archive request/response models.
"""
from dataclasses import dataclass
from typing import List, Optional
from .weather import DateRange


@dataclass
class ArchiveRequest:
    """Request parameters for archive data."""
    spot_id: int
    model_id: int
    date_range: DateRange
    variables: List[str]
    step_hours: int = 2

    @classmethod
    def create(cls, spot_id: int, model_id: int, date_range: DateRange,
               include_wind: bool = True, include_temp: bool = True,
               include_gusts: bool = False) -> 'ArchiveRequest':
        """Create archive request with common parameters."""
        variables = []
        if include_wind:
            variables.extend(['WINDSPD', 'WINDDIR'])
        if include_temp:
            variables.append('TMP')
        if include_gusts:
            variables.append('GUST')

        return cls(
            spot_id=spot_id,
            model_id=model_id,
            date_range=date_range,
            variables=variables
        )


@dataclass
class ArchiveResponse:
    """Response from archive API."""
    html_content: str
    success: bool
    error: Optional[str] = None

    @property
    def has_data(self) -> bool:
        """Check if response contains data."""
        return self.success and bool(self.html_content)
