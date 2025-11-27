# Windguru Archive Browser

🪁🌊A Kitesurfers best friend🪁🌊

Command-line tool for fetching and visualizing historical wind data from Windguru. Inspired by https://github.com/jeremysolarz/windguru-date-cli

## What It Does

This tool allows you to:
- **Fetch historical weather data** from Windguru's archive (wind speed, direction, temperature)
- **Search for spots** by name - no need to know IDs
- **Select date ranges** - analyze any time period
- **Generate interactive visualizations** - dashboard, wind rose, and heatmap charts

Perfect for kitesurfers, windsurfers, and anyone analyzing wind patterns.

### Two Interfaces Available

- **TUI (Terminal UI)**: Modern, interactive terminal interface with Textual (default)
  - Visual spot selection with keyboard navigation (↑↓ arrows, Space to select)
  - Multi-select support for comparing spots
  - Real-time validation and progress feedback
- **CLI**: Classic command-line interface for scripts and automation

## Installation & Usage

### Local Setup

**Requirements:** [uv](https://docs.astral.sh/uv/) (handles Python and dependencies automatically)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Clone the repository
git clone https://github.com/fgeck/windguru-archive-browser.git
cd windguru-archive-browser

# Run the tool (uv handles everything)
uv run python windguru.py           # Modern TUI interface (default)
# or
uv run python windguru.py --cli     # Classic CLI interface
```

### Docker Setup

```bash
# Build the image
docker build -t windguru-archive-browser .

# Run interactively
docker run -it windguru-archive-browser

# Save visualizations to your local machine
docker run -it -v $(pwd)/output:/app/output windguru-archive-browser
```

## How It Works

### TUI Workflow (Default)

When you run the tool with TUI (default), you'll see modern interactive screens:

1. **Login Screen** - Visual form for Windguru credentials
   - Credentials are **securely cached** in your system keyring
   - On subsequent runs, click "Use Saved Credentials" button
   - Option to clear saved credentials if needed

2. **Spot Search Screen** - Interactive spot finder
   - Type spot name and press Search button
   - Navigate results with ↑↓ arrow keys
   - Press Space to select multiple spots
   - Press Enter to proceed with selected spots

3. **Data Fetch Screen** - Configure your data request
   - Select weather model from dropdown (default: GFS 13 km)
   - Enter date range (e.g., `2024-05` or `2024-05-15`)
   - Click "Fetch & Visualize" button
   - View real-time progress in log output
   - Dashboard automatically opens in browser

### CLI Workflow

For the classic CLI interface (`--cli` flag), you'll be prompted step-by-step:

```
🌊 WINDGURU DATA ANALYZER 🌊

Choose login method:
  1. Auto-login (recommended)
  2. Manual cookies

> 1

Email: user@example.com
Password: ********
✅ Successfully logged in!

Search for a spot: Tarifa
✅ Found 8 spots - select one

Choose model (press Enter for default GFS 13 km): [Enter]

From (e.g., 2024-05): 2024-07
To (e.g., 2024-08): 2024-07

⏳ Fetching data...
✅ Fetched 744 data points!
📊 Creating visualizations...
✅ SUCCESS! Opening dashboard in browser...
```

## Output

An interactive HTML dashboard is generated with two panels:

- **Wind Speed & Direction** - Timeline showing wind speed with color-coded zones and direction arrows
- **Temperature** - Timeline showing temperature trends

The file is saved to `output/` directory with a timestamp and automatically opens in your browser.

## Security

### Credential Storage

Credentials are stored securely using your system's native credential manager:
- **macOS**: Keychain
- **Windows**: Windows Credential Locker
- **Linux**: Secret Service (requires libsecret)

**How it works:**
- Only authentication tokens (idu and login_md5) are cached, never passwords
- Cached credentials are validated before each use
- Expired credentials are automatically cleared and you're prompted to log in again
- You can manually clear credentials anytime with option 3

## Requirements

- Windguru account (free or PRO)
- Python 3.9+ (automatically managed by uv)

## Dependencies

- requests - HTTP client
- beautifulsoup4 - HTML parsing
- pandas - Data processing
- plotly - Interactive visualizations

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests with coverage
uv run pytest tests/ -v --cov=src

# Generate HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html
```

### Linting and Type Checking

```bash
# Install linting tools
uv pip install ruff mypy

# Run ruff linter
ruff check src/ tests/

# Run mypy type checker
mypy src/ --ignore-missing-imports
```

### Building

```bash
# Build package (creates wheel and source distribution)
uv build

# Build Docker image
docker build -t windguru-archive-browser .
```

## CI/CD Pipeline

This project includes a comprehensive GitHub Actions pipeline that:

1. **Tests** - Runs tests on Python 3.9, 3.10, 3.11, and 3.12
2. **Linting** - Checks code quality with ruff and mypy
3. **Build** - Creates distributable packages
4. **Docker** - Builds and publishes Docker images to GitHub Container Registry
5. **Release** - Automatically creates GitHub releases for version tags

### Triggering Releases

To create a new release:

```bash
# Tag a new version
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

The CI/CD pipeline will automatically:
- Run all tests
- Build the package
- Create a Docker image tagged with the version
- Create a GitHub release with artifacts

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made for wind sports enthusiasts** 🌊🏄‍♂️
