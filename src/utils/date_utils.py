"""
Date parsing and manipulation utilities.
"""
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from ..models.weather import DateRange


def parse_date_input(date_str: str) -> date:
    """
    Parse date string in YYYY-MM or YYYY-MM-DD format.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed date

    Raises:
        ValueError: If date format is invalid
    """
    date_str = date_str.strip()

    # Try YYYY-MM format first
    if len(date_str) == 7:
        try:
            return datetime.strptime(date_str + '-01', '%Y-%m-%d').date()
        except ValueError:
            pass

    # Try YYYY-MM-DD format
    if len(date_str) == 10:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM or YYYY-MM-DD")


def get_last_day_of_month(year: int, month: int) -> date:
    """
    Get the last day of a given month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Last day of the month
    """
    # Get first day of next month and subtract one day
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    last_day = next_month - relativedelta(days=1)
    return last_day.date()


def parse_date_range_input(from_str: str, to_str: str) -> DateRange:
    """
    Parse date range from user input strings.

    Args:
        from_str: Start date string (YYYY-MM or YYYY-MM-DD)
        to_str: End date string (YYYY-MM or YYYY-MM-DD)

    Returns:
        DateRange object

    Raises:
        ValueError: If dates are invalid or end is before start
    """
    # Parse start date
    start = parse_date_input(from_str)

    # Parse end date
    if len(to_str.strip()) == 7:  # YYYY-MM format
        # Use last day of month for end date
        year, month = map(int, to_str.split('-'))
        end = get_last_day_of_month(year, month)
    else:
        end = parse_date_input(to_str)

    # Create and validate date range
    return DateRange(start=start, end=end)
