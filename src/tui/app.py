"""
Main Textual TUI application for Windguru Archive Browser.
"""
import webbrowser
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Log, OptionList, Select
from textual.widgets.option_list import Option

from ..config.constants import WEATHER_MODELS
from ..config.settings import Settings
from ..models.auth import AuthCredentials
from ..models.spot import Spot
from ..models.weather import WeatherModel
from ..services.archive_service import ArchiveService
from ..services.auth_service import AuthService
from ..services.credential_storage import CredentialStorage
from ..services.spot_service import SpotService
from ..services.visualization_service import VisualizationService
from ..utils.date_utils import parse_date_range_input
from ..utils.stats_utils import format_stats


class LoginScreen(Screen):
    """Login screen for authentication."""

    CSS = """
    LoginScreen {
        align: center middle;
    }

    #login_container {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .success {
        color: $success;
        text-align: center;
        margin: 1 0;
    }

    .divider {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }

    Input {
        margin: 1 0;
    }
    """

    def __init__(self, has_saved_creds: bool = False) -> None:
        """Initialize login screen."""
        super().__init__()
        self.has_saved_creds = has_saved_creds

    def compose(self) -> ComposeResult:
        """Create UI components."""
        with Container(id="login_container"):
            yield Label("🌊 Windguru Archive Browser 🌊", id="title")

            if self.has_saved_creds:
                yield Label("✅ Found saved credentials!", classes="success")
                yield Button("Use Saved Credentials", id="use_saved", variant="primary")
                yield Label("— OR —", classes="divider")

            yield Label("Enter your Windguru credentials:")
            yield Input(placeholder="Email/Username", id="email")
            yield Input(placeholder="Password", password=True, id="password")
            yield Button("Login", id="login", variant="success")

            if self.has_saved_creds:
                yield Button("Clear Saved Credentials", id="clear_saved", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "use_saved":
            self.dismiss(("cached", None, None))
        elif event.button.id == "login":
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            if email and password:
                self.dismiss(("auto", email, password))
        elif event.button.id == "clear_saved":
            CredentialStorage.clear_credentials()
            self.app.notify("Saved credentials cleared!", severity="information")
            self.app.pop_screen()


class SpotSearchScreen(Screen):
    """Screen for searching and selecting spots."""

    CSS = """
    SpotSearchScreen {
        align: center middle;
    }

    #search_container {
        width: 80;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 2;
    }

    #spot_list {
        height: 20;
        border: solid $primary;
        margin: 1 0;
    }

    #help_text {
        color: $text-muted;
        text-align: center;
        margin: 1 0;
    }
    """

    def __init__(self, spot_service: SpotService) -> None:
        """Initialize spot search screen."""
        super().__init__()
        self.spot_service = spot_service
        self.spots: list[Spot] = []
        self.selected_indices: set[int] = set()

    def compose(self) -> ComposeResult:
        """Create UI components."""
        with Container(id="search_container"):
            yield Label("🔍 Search for a Spot", classes="title")
            yield Input(placeholder="Enter spot name (e.g., Tarifa, Theologos)", id="search_input")
            yield Button("Search", id="search_btn", variant="primary")
            yield Label("Use ↑↓ arrows to navigate, Space to toggle selection, Enter to proceed", id="help_text")
            yield OptionList(id="spot_list")
            yield Label("Selected: None", id="selection_count")
            yield Horizontal(
                Button("Continue with Selected", id="select_btn", variant="success", disabled=True),
                Button("Back", id="back_btn"),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search_btn":
            self.search_spots()
        elif event.button.id == "select_btn":
            self.select_spots()
        elif event.button.id == "back_btn":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "search_input":
            self.search_spots()

    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "space":
            # Toggle selection on current highlighted item
            option_list = self.query_one("#spot_list", OptionList)
            if option_list.highlighted is not None:
                idx = option_list.highlighted
                if idx in self.selected_indices:
                    self.selected_indices.remove(idx)
                else:
                    self.selected_indices.add(idx)

                # Update the visual display
                current_highlight = idx
                self.update_selection_display()

                # Restore highlight position
                if current_highlight < len(self.spots):
                    option_list.highlighted = current_highlight

                event.prevent_default()
                event.stop()

    def update_selection_display(self) -> None:
        """Update the selection count display and button state."""
        count = len(self.selected_indices)
        count_label = self.query_one("#selection_count", Label)

        if count == 0:
            count_label.update("Selected: None")
            self.query_one("#select_btn", Button).disabled = True
        elif count == 1:
            count_label.update("Selected: 1 spot")
            self.query_one("#select_btn", Button).disabled = False
        else:
            count_label.update(f"Selected: {count} spots")
            self.query_one("#select_btn", Button).disabled = False

        # Update option list to show selected items with checkmark
        option_list = self.query_one("#spot_list", OptionList)
        option_list.clear_options()
        for i, spot in enumerate(self.spots):
            prefix = "✓ " if i in self.selected_indices else "  "
            option_list.add_option(Option(f"{prefix}{spot}", id=str(i)))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection with Enter key - proceed with selected spots."""
        if self.selected_indices:
            self.select_spots()
        elif self.spots and event.option_index < len(self.spots):
            # If nothing selected but user pressed Enter, select current and proceed
            self.selected_indices.add(event.option_index)
            self.select_spots()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle option highlighting (navigation)."""
        pass  # No action needed, just for navigation

    def search_spots(self) -> None:
        """Search for spots."""
        query = self.query_one("#search_input", Input).value
        if not query:
            self.app.notify("Please enter a search term", severity="warning")
            return

        self.app.notify(f"Searching for '{query}'...", severity="information")
        result = self.spot_service.search(query)

        option_list = self.query_one("#spot_list", OptionList)
        option_list.clear_options()

        if not result.spots:
            self.app.notify("No spots found. Try a different search term.", severity="warning")
            self.query_one("#select_btn", Button).disabled = True
            return

        self.spots = result.spots
        self.selected_indices.clear()
        self.app.notify(f"Found {len(self.spots)} spots!", severity="information")

        # Add spots to option list
        for i, spot in enumerate(self.spots):
            option_list.add_option(Option(f"  {spot}", id=str(i)))

        # Focus the option list for keyboard navigation
        option_list.focus()
        self.update_selection_display()

    def select_spots(self) -> None:
        """Select the spots from selected_indices."""
        if not self.selected_indices:
            self.app.notify("Please select at least one spot", severity="warning")
            return

        # Get the selected spots
        selected_spots = [self.spots[idx] for idx in sorted(self.selected_indices)]

        if len(selected_spots) == 1:
            # Single spot selected - return it directly
            self.dismiss(selected_spots[0])
        else:
            # Multiple spots selected - for now, just use the first one
            # TODO: Handle multiple spots (maybe fetch data for all and combine?)
            self.app.notify(f"Selected {len(selected_spots)} spots, using: {selected_spots[0].name}",
                          severity="information")
            self.dismiss(selected_spots[0])


class DataFetchScreen(Screen):
    """Screen for configuring and fetching data."""

    CSS = """
    DataFetchScreen {
        align: center middle;
    }

    #fetch_container {
        width: 70;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 2;
    }

    #log {
        height: 8;
        border: solid $primary;
        margin: 1 0;
    }

    DataFetchScreen Label {
        margin: 1 0 0 0;
    }

    DataFetchScreen Select {
        margin: 0 0 1 0;
    }

    DataFetchScreen Input {
        margin: 0 0 1 0;
    }
    """

    def __init__(self, spot: Spot, archive_service: ArchiveService, viz_service: VisualizationService) -> None:
        """Initialize data fetch screen."""
        super().__init__()
        self.spot = spot
        self.archive_service = archive_service
        self.viz_service = viz_service

    def compose(self) -> ComposeResult:
        """Create UI components."""
        with Container(id="fetch_container"):
            yield Label(f"📊 Fetch Data for: {self.spot.name}", classes="title")

            yield Label("Weather Model:")
            model_options = [(m['name'], str(m['id'])) for m in WEATHER_MODELS]
            yield Select(model_options, id="model_select", value="3")

            yield Label("Date Range:")
            yield Input(placeholder="From (e.g., 2024-05 or 2024-05-01)", id="date_from")
            yield Input(placeholder="To (e.g., 2024-06 or 2024-06-10)", id="date_to")

            yield Horizontal(
                Button("Fetch & Visualize", id="fetch_btn", variant="success"),
                Button("Back", id="back_btn"),
            )

            yield Log(id="log")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "fetch_btn":
            self.fetch_data()
        elif event.button.id == "back_btn":
            self.dismiss(False)

    def fetch_data(self) -> None:
        """Fetch and visualize data."""
        from ..models.archive import ArchiveRequest

        log = self.query_one("#log", Log)
        log.clear()

        # Get inputs
        model_id = int(self.query_one("#model_select", Select).value)
        date_from = self.query_one("#date_from", Input).value
        date_to = self.query_one("#date_to", Input).value

        if not date_from or not date_to:
            self.app.notify("Please enter both dates", severity="error")
            return

        try:
            # Parse date range
            log.write_line("Parsing date range...")
            date_range = parse_date_range_input(date_from, date_to)
            log.write_line(f"✅ Date range: {date_range}\n")

            # Find model name
            model = next((WeatherModel(**m) for m in WEATHER_MODELS if m['id'] == model_id), None)
            model_name = model.name if model else f"Model {model_id}"

            # Fetch data
            log.write_line("📥 Fetching data from Windguru...")
            log.write_line(f"   Spot: {self.spot.name}")
            log.write_line(f"   Model: {model_name}")
            log.write_line(f"   Dates: {date_range}\n")

            request = ArchiveRequest.create(
                spot_id=self.spot.id,
                model_id=model_id,
                date_range=date_range,
                include_wind=True,
                include_temp=True
            )

            weather_data = self.archive_service.get_weather_data(
                request,
                spot_name=self.spot.name,
                model_name=model_name
            )

            log.write_line(f"✅ Fetched {weather_data.record_count} data points!\n")

            # Display statistics
            log.write_line("📊 Weather Statistics:")
            stats = weather_data.get_summary_stats()
            stats_text = format_stats(stats)
            for line in stats_text.split('\n'):
                log.write_line(f"   {line}")

            # Create visualization
            log.write_line("\n📈 Creating interactive dashboard...")
            dashboard_file = self.viz_service.create_dashboard(weather_data)
            log.write_line(f"✅ Dashboard created: {dashboard_file.name}\n")

            # Open in browser
            webbrowser.open(f"file://{dashboard_file.absolute()}")
            log.write_line("🌐 Opened dashboard in browser!")

            self.app.notify("Success! Dashboard created and opened.", severity="information")

        except Exception as e:
            log.write_line(f"\n❌ Error: {str(e)}")
            self.app.notify(f"Error: {str(e)}", severity="error")


class WindguruTUI(App):
    """Main Textual TUI application."""

    CSS = """
    Screen {
        background: $background;
    }

    .title {
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }

    .success {
        color: $success;
        text-align: center;
    }

    .divider {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }

    /* Global button styling to ensure text is visible */
    Button {
        width: auto;
        height: 3;
        min-width: 16;
        padding: 0 2;
        margin: 1 0;
        border: tall $background;
        content-align: center middle;
    }

    Button:focus {
        text-style: bold;
        border: tall $accent;
    }

    Button:hover {
        border: tall $primary;
    }

    Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    Horizontal > Button {
        margin: 0 2;
    }
    """

    TITLE = "Windguru Archive Browser"
    SUB_TITLE = "Historical Wind Data Visualization"

    def __init__(self) -> None:
        """Initialize TUI application."""
        super().__init__()
        self.settings = Settings.load()
        self.credentials: Optional[AuthCredentials] = None
        self.auth_service: Optional[AuthService] = None
        self.spot_service: Optional[SpotService] = None
        self.archive_service: Optional[ArchiveService] = None
        self.viz_service: Optional[VisualizationService] = None

    def compose(self) -> ComposeResult:
        """Create UI components."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount - start login flow."""
        self.run_login()

    def run_login(self) -> None:
        """Run login flow."""
        has_saved = CredentialStorage.has_saved_credentials()
        self.push_screen(LoginScreen(has_saved), self.handle_login)

    def handle_login(self, result: tuple) -> None:
        """Handle login result."""
        if result is None:
            self.exit()
            return

        method, email, password = result

        if method == "cached":
            # Use cached credentials
            creds = CredentialStorage.get_credentials()
            if not creds:
                self.notify("Failed to load saved credentials", severity="error")
                self.run_login()
                return

            self.credentials = creds
            self.auth_service = AuthService()

            # Validate credentials
            self.notify("Validating credentials...", severity="information")
            if not self.auth_service.validate_credentials(self.credentials):
                self.notify("Saved credentials are invalid! Clearing...", severity="error")
                CredentialStorage.clear_credentials()
                self.run_login()
                return

            self.notify("Credentials validated!", severity="information")
            self.initialize_services()
            self.run_spot_search()

        elif method == "auto":
            # Auto-login
            self.auth_service = AuthService()
            self.notify("Connecting to Windguru...", severity="information")

            response = self.auth_service.login(email, password)

            if not response.success:
                self.notify(f"Login failed: {response.error}", severity="error")
                self.run_login()
                return

            self.credentials = response.credentials
            self.notify("Successfully logged in!", severity="information")

            # Save credentials
            CredentialStorage.save_credentials(self.credentials, username=email)
            self.notify("Credentials saved!", severity="information")

            self.initialize_services()
            self.run_spot_search()

    def initialize_services(self) -> None:
        """Initialize all services."""
        self.spot_service = SpotService(self.credentials)
        self.archive_service = ArchiveService(self.credentials)
        self.viz_service = VisualizationService(self.settings.output_dir)

    def run_spot_search(self) -> None:
        """Run spot search flow."""
        self.push_screen(SpotSearchScreen(self.spot_service), self.handle_spot_selection)

    def handle_spot_selection(self, spot: Optional[Spot]) -> None:
        """Handle spot selection result."""
        if spot is None:
            self.exit()
            return

        self.notify(f"Selected: {spot.name}", severity="information")
        self.push_screen(
            DataFetchScreen(spot, self.archive_service, self.viz_service),
            self.handle_data_fetch
        )

    def handle_data_fetch(self, success: bool) -> None:
        """Handle data fetch result."""
        if not success:
            self.run_spot_search()


def run_tui() -> None:
    """Run the Textual TUI application."""
    app = WindguruTUI()
    app.run()
