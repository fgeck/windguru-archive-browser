# Project Instructions for Claude Code

## Testing Policy

You are encouraged and expected to test Python code in this repository:

- Run `uv run pytest tests/ -v` to execute all tests
- Tests are located in the `tests/` directory
- Current test coverage: 73%
- All tests must pass before committing changes
- Use `pytest-mock` for mocking external dependencies

## Development Workflow

### Running Tests
```bash
uv run pytest tests/ -v --cov=src
```

### Linting
```bash
ruff check src/ tests/
mypy src/ --ignore-missing-imports
```

### Building
```bash
uv build
```

## Code Standards

- Python 3.9+ compatibility required
- Type hints are mandatory for all functions
- Follow PEP 8 style guidelines (enforced by ruff)
- Maintain test coverage above 70%

## CI/CD

The project uses GitHub Actions for:
- Automated testing on multiple Python versions
- Code quality checks (ruff, mypy)
- Package building
- Docker image publishing
- Automated releases

## Project Structure

- `src/` - Main application code
- `tests/` - Unit tests
- `windguru.py` - Entry point
- `.github/workflows/` - CI/CD pipelines
