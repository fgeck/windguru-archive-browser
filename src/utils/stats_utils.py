"""
Statistics formatting and display utilities.
"""
from typing import Any

from ..models.weather import WeatherData


def format_stats(stats: dict[str, Any]) -> str:
    """
    Format statistics dictionary into readable string.

    Args:
        stats: Statistics dictionary from WeatherData.get_summary_stats()

    Returns:
        Formatted string
    """
    lines = []

    if 'wind_speed' in stats:
        ws = stats['wind_speed']
        lines.append("WIND SPEED (knots)")
        lines.append(f"  Mean:    {ws['mean']:.1f}")
        lines.append(f"  Median:  {ws['median']:.1f}")
        lines.append(f"  Min:     {ws['min']:.1f}")
        lines.append(f"  Max:     {ws['max']:.1f}")
        lines.append("")

    if 'wind_ranges' in stats:
        wr = stats['wind_ranges']
        lines.append("FAVORABLE CONDITIONS (% of time)")
        lines.append(f"  10-20 knots: {wr['10-20_knots']:.1f}%")
        lines.append(f"  15-25 knots: {wr['15-25_knots']:.1f}%")
        lines.append(f"  20-30 knots: {wr['20-30_knots']:.1f}%")
        lines.append("")

    if 'temperature' in stats:
        temp = stats['temperature']
        lines.append("TEMPERATURE (°C)")
        lines.append(f"  Mean:    {temp['mean']:.1f}")
        lines.append(f"  Median:  {temp['median']:.1f}")
        lines.append(f"  Min:     {temp['min']:.1f}")
        lines.append(f"  Max:     {temp['max']:.1f}")

    return "\n".join(lines)


def print_weather_stats(weather_data: WeatherData) -> None:
    """
    Print formatted weather statistics to console.

    Args:
        weather_data: Weather data to print stats for
    """
    spot_name = weather_data.spot_name or f"Spot {weather_data.spot_id}"

    print("\n" + "=" * 60)
    print(f"Wind Statistics for {spot_name}")
    print("=" * 60)
    print(f"Date Range: {weather_data.date_range}")
    print(f"Total Records: {weather_data.record_count}")
    print()
    print("-" * 60)

    stats = weather_data.get_summary_stats()
    print(format_stats(stats))

    print("=" * 60)
