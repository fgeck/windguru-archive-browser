#!/usr/bin/env python3
"""
Windguru Archive Browser - Main entry point

A user-friendly interface for fetching and visualizing
historical Windguru weather data.

Usage:
    python windguru.py           # Run TUI (default)
    python windguru.py --cli     # Run classic CLI
    python windguru.py --tui     # Run TUI explicitly

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
from src.tui.app import run_tui
from src.config.settings import Settings


def main() -> None:
    """Main entry point."""
    # Check command line arguments
    use_cli = '--cli' in sys.argv
    use_tui = '--tui' in sys.argv or (not use_cli)  # TUI is default

    if use_tui:
        # Run modern TUI
        try:
            run_tui()
        except KeyboardInterrupt:
            print("\n\n👋 Bye!")
            sys.exit(0)
    else:
        # Run classic CLI
        settings = Settings.load()
        cli = WindguruCLI(settings)
        cli.run()


if __name__ == "__main__":
    main()
