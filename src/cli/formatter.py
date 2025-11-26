"""
CLI formatting utilities.
"""


class CLIFormatter:
    """Handles formatting of CLI output."""

    @staticmethod
    def header(text: str, width: int = 60) -> str:
        """Create a header."""
        return f"\n{'=' * width}\n{text}\n{'=' * width}"

    @staticmethod
    def subheader(text: str, width: int = 60) -> str:
        """Create a subheader."""
        return f"\n{'-' * width}\n{text}\n{'-' * width}"

    @staticmethod
    def success(message: str) -> str:
        """Format success message."""
        return f"✅ {message}"

    @staticmethod
    def error(message: str) -> str:
        """Format error message."""
        return f"❌ {message}"

    @staticmethod
    def info(message: str) -> str:
        """Format info message."""
        return f"ℹ️  {message}"

    @staticmethod
    def working(message: str) -> str:
        """Format working/progress message."""
        return f"🔄 {message}"

    @staticmethod
    def section_break(width: int = 60) -> str:
        """Create a section break."""
        return "\n" + "=" * width + "\n"
