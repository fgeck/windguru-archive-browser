"""
File utilities.
"""
import re
from datetime import datetime
from pathlib import Path


def generate_safe_filename(spot_name: str, suffix: str = "", extension: str = "html") -> str:
    """
    Generate a safe filename from spot name.

    Args:
        spot_name: Spot name
        suffix: Optional suffix to add
        extension: File extension (default: html)

    Returns:
        Safe filename with timestamp
    """
    # Remove unsafe characters
    safe_name = re.sub(r'[^\w\s-]', '', spot_name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)

    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build filename
    parts = [safe_name, timestamp]
    if suffix:
        parts.append(suffix)

    filename = "_".join(parts) + f".{extension}"
    return filename


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists.

    Args:
        path: Directory path

    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
