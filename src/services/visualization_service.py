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

        # Calculate initial averages for the full dataset
        wind_avg = df['wind_speed'].mean() if weather_data.has_wind_speed else None
        temp_avg = df['temperature'].mean() if weather_data.has_temperature else None

        # Add initial average annotations
        if wind_avg is not None:
            fig.add_annotation(
                text=f'Avg: {wind_avg:.1f} knots',
                xref='paper', yref='paper',
                x=0.02, y=0.98,
                xanchor='left', yanchor='top',
                showarrow=False,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#1f77b4',
                borderwidth=2,
                borderpad=4,
                font=dict(size=14, color='#1f77b4', family='Arial, sans-serif'),
                name='wind_avg'
            )

        if temp_avg is not None:
            fig.add_annotation(
                text=f'Avg: {temp_avg:.1f}°C',
                xref='paper', yref='paper',
                x=0.02, y=0.36,
                xanchor='left', yanchor='top',
                showarrow=False,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#d62728',
                borderwidth=2,
                borderpad=4,
                font=dict(size=14, color='#d62728', family='Arial, sans-serif'),
                name='temp_avg'
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
            hovermode='x unified',
            # Add modebar buttons for displaying statistics
            modebar_add=['v1hovermode', 'toggleSpikeLines']
        )

        # Add JavaScript for updating averages on zoom
        avg_script = """
        <script>
        (function() {
            function waitForPlotly() {
                var graphDiv = document.getElementById('{plot_div_id}');
                if (!graphDiv || !window.Plotly) {
                    setTimeout(waitForPlotly, 100);
                    return;
                }

                var isUpdating = false;

                function calculateAverage(data, xaxis_range) {
                    if (!data || !data.x || data.x.length === 0) return null;

                    var x = data.x;
                    var y = data.y;
                    var sum = 0;
                    var count = 0;

                    for (var i = 0; i < x.length; i++) {
                        var xval = new Date(x[i]).getTime();
                        var x0 = new Date(xaxis_range[0]).getTime();
                        var x1 = new Date(xaxis_range[1]).getTime();

                        if (xval >= x0 && xval <= x1 && y[i] !== null && y[i] !== undefined && !isNaN(y[i])) {
                            sum += y[i];
                            count++;
                        }
                    }

                    return count > 0 ? sum / count : null;
                }

                function updateAverages() {
                    if (!graphDiv || !graphDiv.layout || !graphDiv.data || isUpdating) return;

                    isUpdating = true;

                    try {
                        var xaxis1_range = graphDiv.layout.xaxis.range;
                        var xaxis2_range = graphDiv.layout.xaxis2.range;

                        // Get all existing annotations
                        var annotations = (graphDiv.layout.annotations || []).slice();

                        // Remove only the average annotations (keep wind zones and other annotations)
                        var filteredAnnotations = [];
                        for (var i = 0; i < annotations.length; i++) {
                            var ann = annotations[i];
                            // Keep annotation if it doesn't contain "Avg:" text
                            if (!ann.text || ann.text.indexOf('Avg:') === -1) {
                                filteredAnnotations.push(ann);
                            }
                        }

                        // Calculate and add wind speed average
                        if (graphDiv.data[0] && xaxis1_range) {
                            var windAvg = calculateAverage(graphDiv.data[0], xaxis1_range);
                            if (windAvg !== null) {
                                filteredAnnotations.push({
                                    text: 'Avg: ' + windAvg.toFixed(1) + ' knots',
                                    xref: 'paper',
                                    yref: 'paper',
                                    x: 0.02,
                                    y: 0.98,
                                    xanchor: 'left',
                                    yanchor: 'top',
                                    showarrow: false,
                                    bgcolor: 'rgba(255, 255, 255, 0.9)',
                                    bordercolor: '#1f77b4',
                                    borderwidth: 2,
                                    borderpad: 4,
                                    font: {size: 14, color: '#1f77b4'}
                                });
                            }
                        }

                        // Calculate and add temperature average
                        for (var i = 0; i < graphDiv.data.length; i++) {
                            if (graphDiv.data[i].name === 'Temperature' && xaxis2_range) {
                                var tempAvg = calculateAverage(graphDiv.data[i], xaxis2_range);
                                if (tempAvg !== null) {
                                    filteredAnnotations.push({
                                        text: 'Avg: ' + tempAvg.toFixed(1) + '°C',
                                        xref: 'paper',
                                        yref: 'paper',
                                        x: 0.02,
                                        y: 0.36,
                                        xanchor: 'left',
                                        yanchor: 'top',
                                        showarrow: false,
                                        bgcolor: 'rgba(255, 255, 255, 0.9)',
                                        bordercolor: '#d62728',
                                        borderwidth: 2,
                                        borderpad: 4,
                                        font: {size: 14, color: '#d62728'}
                                    });
                                }
                                break;
                            }
                        }

                        // Update the layout with all annotations
                        Plotly.relayout(graphDiv, {annotations: filteredAnnotations}).then(function() {
                            isUpdating = false;
                        }).catch(function(err) {
                            console.error('Error updating averages:', err);
                            isUpdating = false;
                        });
                    } catch(e) {
                        console.error('Error updating averages:', e);
                        isUpdating = false;
                    }
                }

                // Update on relayout events (zoom, pan, etc)
                graphDiv.on('plotly_relayout', function(eventdata) {
                    // Skip if we're currently updating to avoid infinite loops
                    if (isUpdating) return;

                    // Check if this is a zoom/pan event (not triggered by our own relayout)
                    if (eventdata['xaxis.range[0]'] !== undefined ||
                        eventdata['xaxis2.range[0]'] !== undefined ||
                        eventdata['xaxis.autorange'] !== undefined ||
                        eventdata['xaxis2.autorange'] !== undefined) {
                        setTimeout(updateAverages, 100);
                    }
                });
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', waitForPlotly);
            } else {
                waitForPlotly();
            }
        })();
        </script>
        """

        # Save
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() else '_' for c in spot_name)
            output_file = self.output_dir / f"{safe_name}_{timestamp}_dashboard.html"

        # Write HTML with include_plotlyjs='cdn' to reduce file size
        fig.write_html(str(output_file), include_plotlyjs='cdn')

        # Read the HTML file and inject the JavaScript
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Find the plot div ID - Plotly typically uses a specific pattern
        import re
        # Try multiple patterns to find the div
        plot_div_match = re.search(r'<div id="([^"]+)"\s+class="plotly-graph-div"', html_content)
        if not plot_div_match:
            plot_div_match = re.search(r'<div id="([^"]+)"[^>]*class="plotly-graph-div"', html_content)
        if not plot_div_match:
            plot_div_match = re.search(r'<div[^>]+id="([^"]+)"[^>]*>', html_content)

        if plot_div_match:
            plot_div_id = plot_div_match.group(1)
            print(f"Found plot div ID: {plot_div_id}")

            # Inject the script before closing body tag
            script_with_id = avg_script.replace('{plot_div_id}', plot_div_id)

            if '</body>' in html_content:
                html_content = html_content.replace('</body>', f'{script_with_id}</body>')
                print("Injected JavaScript before </body> tag")
            else:
                # If no body tag, append at the end
                html_content += script_with_id
                print("Appended JavaScript at end of file")

            # Write back the modified HTML
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        else:
            print("WARNING: Could not find plot div ID, JavaScript not injected")

        return output_file
