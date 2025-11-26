"""
Application settings.
"""
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings."""
    output_dir: Path = Path('output')
    default_model_id: int = 3  # GFS 13km
    step_hours: int = 2
    timeout_seconds: int = 30
    verbose: bool = False

    def __post_init__(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> 'Settings':
        """Load settings from file or use defaults."""
        # For now, just return defaults
        # In the future, could load from config file
        return cls()
