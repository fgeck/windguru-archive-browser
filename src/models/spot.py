"""
Spot-related data models.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Spot:
    """Represents a Windguru spot."""
    id: int
    name: str
    country: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        if self.country:
            return f"{self.country} - {self.name} (ID: {self.id})"
        return f"{self.name} (ID: {self.id})"


@dataclass
class SpotSearchResult:
    """Result from spot search."""
    spots: list[Spot]
    query: str
    total: int

    def __len__(self) -> int:
        """Return number of spots found."""
        return len(self.spots)

    def __iter__(self):
        """Make iterable."""
        return iter(self.spots)
