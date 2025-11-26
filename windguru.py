#!/usr/bin/env python3
"""
Windguru CLI - Main entry point

A user-friendly command-line interface for fetching and visualizing
historical Windguru weather data.

Usage:
    python windguru.py

Or make executable and run directly:
    chmod +x windguru.py
    ./windguru.py
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.cli.app import WindguruCLI
from src.config.settings import Settings


def main() -> None:
    """Main entry point."""
    # Load settings
    settings = Settings.load()

    # Create and run CLI
    cli = WindguruCLI(settings)
    cli.run()


if __name__ == "__main__":
    main()
