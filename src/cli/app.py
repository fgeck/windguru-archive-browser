"""
Main CLI application.
"""
import sys
import webbrowser
from pathlib import Path

from typing import Optional

from ..models.auth import AuthCredentials
from ..models.archive import ArchiveRequest
from ..models.spot import Spot
from ..services.auth_service import AuthService
from ..services.spot_service import SpotService
from ..services.archive_service import ArchiveService
from ..services.visualization_service import VisualizationService
from ..services.credential_storage import CredentialStorage
from ..config.settings import Settings
from ..utils.stats_utils import print_weather_stats
from .prompts import CredentialsPrompt, SpotPrompt, DateRangePrompt, ModelPrompt
from .formatter import CLIFormatter


class WindguruCLI:
    """Main CLI application orchestrator."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize CLI application.

        Args:
            settings: Application settings (uses defaults if not provided)
        """
        self.settings = settings or Settings.load()
        self.fmt = CLIFormatter()
        self.credentials: Optional[AuthCredentials] = None

        # Services (initialized after authentication)
        self.auth_service: Optional[AuthService] = None
        self.spot_service: Optional[SpotService] = None
        self.archive_service: Optional[ArchiveService] = None
        self.viz_service: Optional[VisualizationService] = None

    def print_banner(self) -> None:
        """Print application banner."""
        print("\n" + "🌊" * 30)
        print(" " * 20 + "WINDGURU DATA ANALYZER")
        print("🌊" * 30 + "\n")

    def authenticate(self) -> bool:
        """
        Handle authentication flow.

        Returns:
            True if authentication successful
        """
        email, password, manual_creds, method = CredentialsPrompt.prompt()

        if method in ('auto', 'auto-save'):
            # Auto-login
            self.auth_service = AuthService()
            print(f"\n{self.fmt.working('Connecting to Windguru...')}")

            response = self.auth_service.login(email, password)

            if not response.success:
                print(self.fmt.error(f"Auto-login failed: {response.error}"))
                print("\nYou can:")
                print("  1. Try again with correct credentials")
                print("  2. Restart and use manual method (option 2)")
                return False

            self.credentials = response.credentials
            print(self.fmt.success("Successfully logged in!"))
            print(f"   IDU: {self.credentials.idu}")
            print(f"   login_md5: {self.credentials.login_md5[:20]}...")

            # Save credentials if requested
            if method == 'auto-save':
                CredentialStorage.save_credentials(self.credentials, username=email)
                print(self.fmt.success("Credentials saved securely!"))

        elif method in ('manual', 'manual-save'):
            # Manual login
            self.credentials = manual_creds
            self.auth_service = AuthService()

            # Save credentials if requested
            if method == 'manual-save':
                CredentialStorage.save_credentials(self.credentials)
                print(self.fmt.success("Credentials saved securely!"))

        elif method == 'cached':
            # Use cached credentials
            self.credentials = manual_creds
            self.auth_service = AuthService()
            print(self.fmt.success("Using saved credentials!"))

        # Initialize services
        self.spot_service = SpotService(self.credentials)
        self.archive_service = ArchiveService(self.credentials)
        self.viz_service = VisualizationService(self.settings.output_dir)

        # Establish session
        print(f"\n{self.fmt.working('Establishing session with Windguru...')}")
        if not self.auth_service.establish_session(self.credentials):
            print(self.fmt.error("Failed to establish session"))
            return False

        return True

    def select_spot(self) -> Optional[Spot]:
        """
        Handle spot selection flow.

        Returns:
            Selected Spot or None if failed
        """
        while True:
            query = SpotPrompt.prompt_search()

            if not query:
                print(self.fmt.error("Please enter a search term"))
                continue

            print(f"\n{self.fmt.working(f'Searching for {query!r}...')}")
            results = self.spot_service.search(query)

            if not results.spots:
                print(self.fmt.error("No spots found. Try a different search term."))
                continue

            spot = SpotPrompt.display_results(results.spots)
            if spot:
                return spot
            # If None, loop to search again

    def fetch_and_visualize(self) -> bool:
        """Main workflow: fetch data and create visualizations."""
        try:
            # Select spot
            spot = self.select_spot()
            if not spot:
                return False

            # Select model
            model = ModelPrompt.prompt()

            # Get date range
            date_range = DateRangePrompt.prompt()

            # Fetch data
            print(self.fmt.header("FETCHING DATA"))
            print(f"Spot: {spot.name}")
            print(f"Model: {model.name}")
            print(f"Date Range: {date_range}")
            print(f"\n{self.fmt.working('Fetching data from Windguru (this may take a moment)...')}\n")

            request = ArchiveRequest.create(
                spot_id=spot.id,
                model_id=model.id,
                date_range=date_range,
                include_wind=True,
                include_temp=True
            )

            weather_data = self.archive_service.get_weather_data(
                request,
                spot_name=spot.name,
                model_name=model.name
            )

            print(self.fmt.success(f"Successfully fetched {weather_data.record_count} data points!"))

            # Display statistics
            print_weather_stats(weather_data)

            # Create visualization
            print(self.fmt.header("CREATING VISUALIZATION"))
            print()

            print("📊 Creating interactive dashboard...")
            dashboard_file = self.viz_service.create_dashboard(weather_data)

            # Display results
            print(self.fmt.header("SUCCESS!"))
            print(f"\n📊 Dashboard: file://{dashboard_file.absolute()}")
            print(self.fmt.section_break())

            # Offer to open in browser
            try:
                open_browser = input("Open dashboard in browser now? (y/n): ").strip().lower()
                if open_browser == 'y':
                    webbrowser.open(f"file://{dashboard_file.absolute()}")
                    print(self.fmt.success("Opened in browser!"))
            except:
                pass

            return True

        except Exception as e:
            print(self.fmt.error(f"Error: {e}"))
            if self.settings.verbose:
                import traceback
                traceback.print_exc()
            return False

    def run(self) -> None:
        """Run the CLI application."""
        try:
            self.print_banner()

            # Authenticate
            if not self.authenticate():
                sys.exit(1)

            # Main workflow
            if not self.fetch_and_visualize():
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n👋 Bye!")
            sys.exit(0)
        except Exception as e:
            print(self.fmt.error(f"Unexpected error: {e}"))
            if self.settings.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
