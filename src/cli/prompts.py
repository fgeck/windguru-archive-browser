"""
CLI prompt handlers.
"""
import getpass
from typing import Optional, Tuple

from ..models.auth import AuthCredentials
from ..models.spot import Spot
from ..models.weather import DateRange, WeatherModel
from ..utils.date_utils import parse_date_range_input
from ..config.constants import WEATHER_MODELS
from .formatter import CLIFormatter


class CredentialsPrompt:
    """Handles credential input from user."""

    @staticmethod
    def prompt() -> Tuple[Optional[str], Optional[str], Optional[AuthCredentials], str]:
        """
        Prompt user for credentials.

        Returns:
            Tuple of (email, password, manual_credentials, method)
            - If method='auto': email and password will be set
            - If method='manual': manual_credentials will be set
        """
        fmt = CLIFormatter()

        print(fmt.header("WINDGURU CREDENTIALS"))
        print("Choose login method:")
        print("  1. Auto-login (recommended) - Enter your Windguru username/password")
        print("  2. Manual - Enter idu and login_md5 from browser cookies")
        print()

        while True:
            choice = input("Choose method (1 or 2): ").strip()

            if choice == '1':
                print(fmt.subheader("AUTO LOGIN"))
                print("Your password will not be displayed as you type (hidden input)")
                print()

                email = input("Windguru email: ").strip()
                password = getpass.getpass("Windguru password: ")

                if not email or not password:
                    print(fmt.error("Both email and password are required!"))
                    continue

                return email, password, None, 'auto'

            elif choice == '2':
                print(fmt.subheader("MANUAL METHOD - Extract cookies from browser"))
                print("If auto-login doesn't work, you can manually extract cookies.")
                print()
                print("Step-by-step instructions:")
                print("1. Open https://www.windguru.cz in your browser")
                print("2. Login with your Windguru account")
                print("3. Press F12 (or right-click → Inspect)")
                print("4. Go to the Application tab (Chrome) or Storage tab (Firefox)")
                print("5. Click on 'Cookies' → 'https://www.windguru.cz'")
                print("6. Find and copy these two cookie values:")
                print("   - idu (e.g., '1538171')")
                print("   - login_md5 (long hash like 'fc4224c6eed210ff9b426a3bb1aaf144')")
                print()

                idu = input("Enter your idu: ").strip()
                login_md5 = input("Enter your login_md5: ").strip()

                if not idu or not login_md5:
                    print(fmt.error("Both idu and login_md5 are required!"))
                    continue

                credentials = AuthCredentials(idu=idu, login_md5=login_md5)
                print(fmt.success("Credentials received!"))
                print(f"   IDU: {idu}")
                print(f"   login_md5: {login_md5[:20]}...")

                return None, None, credentials, 'manual'

            else:
                print(fmt.error("Please enter 1 or 2"))


class SpotPrompt:
    """Handles spot selection from user."""

    @staticmethod
    def prompt_search() -> str:
        """
        Prompt user for spot search query.

        Returns:
            Search query string
        """
        fmt = CLIFormatter()
        print(fmt.header("SPOT SEARCH"))
        query = input("\nSearch for a spot (e.g., 'Theologos', 'Tarifa'): ").strip()
        return query

    @staticmethod
    def display_results(spots: list[Spot]) -> Optional[Spot]:
        """
        Display spot search results and let user choose.

        Args:
            spots: List of spots to display

        Returns:
            Selected spot or None if user wants to search again
        """
        fmt = CLIFormatter()

        if not spots:
            print(fmt.error("No spots found. Try a different search term."))
            return None

        print(f"\n{fmt.success(f'Found {len(spots)} spots:')}\n")
        for i, spot in enumerate(spots, 1):
            print(f"  {i}. {spot}")

        print(f"\n  0. Search again")

        while True:
            try:
                choice = input(f"\nChoose a spot (1-{len(spots)}, or 0 to search again): ").strip()
                choice_num = int(choice)

                if choice_num == 0:
                    return None
                elif 1 <= choice_num <= len(spots):
                    selected = spots[choice_num - 1]
                    print(f"\n{fmt.success(f'Selected: {selected.name}')}")
                    return selected
                else:
                    print(fmt.error(f"Please enter a number between 0 and {len(spots)}"))
            except ValueError:
                print(fmt.error("Please enter a valid number"))


class DateRangePrompt:
    """Handles date range input from user."""

    @staticmethod
    def prompt() -> DateRange:
        """
        Prompt user for date range.

        Returns:
            DateRange object
        """
        fmt = CLIFormatter()

        print(fmt.header("DATE RANGE"))
        print("Enter the date range for the data you want to analyze.")
        print("Format: YYYY-MM or YYYY-MM-DD")
        print()

        while True:
            from_str = input("From (e.g., 2024-05 or 2024-05-01): ").strip()
            to_str = input("To (e.g., 2024-06 or 2024-06-10): ").strip()

            try:
                date_range = parse_date_range_input(from_str, to_str)
                print(f"\n{fmt.success(f'Date range: {date_range}')}")
                return date_range
            except ValueError as e:
                print(fmt.error(str(e)))
                continue


class ModelPrompt:
    """Handles weather model selection from user."""

    @staticmethod
    def prompt() -> WeatherModel:
        """
        Prompt user to choose a weather model.

        Returns:
            Selected WeatherModel
        """
        fmt = CLIFormatter()

        print(fmt.header("WEATHER MODEL"))
        print("Choose a weather model:\n")

        models = [WeatherModel(**m) for m in WEATHER_MODELS]

        for i, model in enumerate(models, 1):
            print(f"  {i}. {model.name}")

        while True:
            try:
                choice = input(f"\nChoose a model (1-{len(models)}, or press Enter for default): ").strip()

                if not choice:
                    selected = models[0]
                    print(fmt.success(f"Using default: {selected.name}"))
                    return selected

                choice_num = int(choice)
                if 1 <= choice_num <= len(models):
                    selected = models[choice_num - 1]
                    print(fmt.success(f"Selected: {selected.name}"))
                    return selected
                else:
                    print(fmt.error(f"Please enter a number between 1 and {len(models)}"))
            except ValueError:
                print(fmt.error("Please enter a valid number"))
