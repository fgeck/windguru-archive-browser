"""
Visualization service for creating charts and graphs.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..config.constants import WIND_SPEED_ZONES
from ..models.weather import WeatherData


class VisualizationService:
    """Handles creation of visualizations."""

    def __init__(self, output_dir: Path) -> None:
        """
        Initialize visualization service.

        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_dashboard(self, weather_data: WeatherData,
                        output_file: Optional[Path] = None) -> Path:
        """
        Create interactive dashboard with wind speed (with direction arrows) and temperature.

        Args:
            weather_data: Weather data to visualize
            output_file: Optional custom output file path

        Returns:
            Path to saved HTML file
        """
        df = weather_data.dataframe
        spot_name = weather_data.spot_name or f"Spot {weather_data.spot_id}"

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                f'Wind Speed & Direction - {spot_name}',
                f'Temperature - {spot_name}'
            ),
            vertical_spacing=0.12,
            row_heights=[0.6, 0.4]
        )

        # Wind Speed Plot with Direction Arrows
        if weather_data.has_wind_speed:
            fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['wind_speed'],
                    mode='lines',
                    name='Wind Speed',
                    line={"color": '#1f77b4', "width": 2},
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.3)',
                    hovertemplate='<b>%{x}</b><br>Wind Speed: %{y:.1f} knots<extra></extra>'
                ),
                row=1, col=1
            )

            # Add wind speed zones
            for zone in WIND_SPEED_ZONES:
                fig.add_hrect(
                    y0=zone['min'], y1=zone['max'],
                    line_width=0,
                    fillcolor=zone['color'],
                    opacity=0.1,
                    annotation_text=zone['label'],
                    annotation_position="right",
                    row=1, col=1
                )

            # Add wind direction arrows (sample every Nth point to avoid clutter)
            if weather_data.has_wind_direction:
                arrow_interval = max(1, len(df) // 30)  # Show ~30 arrows max
                df_arrows = df.iloc[::arrow_interval]

                for _, row in df_arrows.iterrows():
                    # Convert wind direction to arrow angle (wind direction is "from", need to show "to")
                    (row['wind_dir'] + 180) % 360 * 3.14159 / 180
                    arrow_length = row['wind_speed'] * 0.3  # Scale arrow by wind speed

                    fig.add_annotation(
                        x=row['datetime'],
                        y=row['wind_speed'],
                        ax=0,
                        ay=arrow_length,
                        xref='x',
                        yref='y',
                        axref='pixel',
                        ayref='pixel',
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor='rgba(50, 50, 50, 0.6)',
                        standoff=0,
                        row=1, col=1
                    )

        # Temperature Plot
        if weather_data.has_temperature:
            fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['temperature'],
                    mode='lines',
                    name='Temperature',
                    line={"color": '#d62728', "width": 2},
                    fill='tozeroy',
                    fillcolor='rgba(214, 39, 40, 0.3)',
                    hovertemplate='<b>%{x}</b><br>Temperature: %{y:.1f}°C<extra></extra>'
                ),
                row=2, col=1
            )

        # Update axes
        fig.update_yaxes(title_text="Wind Speed (knots)", row=1, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)

        # Update layout
        fig.update_layout(
            height=700,
            showlegend=False,
            title_text=f"Weather Data - {spot_name}<br>{weather_data.date_range}",
            hovermode='x unified'
        )

        # Save
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() else '_' for c in spot_name)
            output_file = self.output_dir / f"{safe_name}_{timestamp}_dashboard.html"

        fig.write_html(str(output_file))
        return output_file
