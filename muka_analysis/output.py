"""
Output abstraction interface for MuKa farm analysis.

This module provides a centralized interface for all console output, logging,
and user interactions using Rich and Typer. It supports theme switching,
consistent color management, and abstracted output methods.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.theme import Theme
from rich.traceback import install as install_rich_traceback


class ColorScheme(str, Enum):
    """Available color schemes for the application."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeColors(BaseModel):
    """Color definitions for a theme."""

    success: str = Field(..., description="Color for success messages")
    error: str = Field(..., description="Color for error messages")
    warning: str = Field(..., description="Color for warning messages")
    info: str = Field(..., description="Color for informational messages")
    data: str = Field(..., description="Color for data display")
    highlight: str = Field(..., description="Color for highlighting")
    header: str = Field(..., description="Color for headers")
    progress: str = Field(..., description="Color for progress indicators")


class OutputInterface:
    """
    Centralized output interface for all console interactions.

    This class provides a unified API for:
    - Console output with consistent styling
    - Logging with Rich handlers
    - Progress tracking
    - User prompts and confirmations
    - Table rendering
    - Error display

    Attributes:
        console: Rich console instance
        theme_colors: Current theme colors
        color_scheme: Active color scheme

    Example:
        >>> output = OutputInterface(color_scheme=ColorScheme.DARK)
        >>> output.success("Operation completed successfully!")
        >>> output.error("Something went wrong")
        >>> if output.confirm("Continue?"):
        ...     output.info("Proceeding...")
    """

    # Theme definitions
    THEMES: Dict[ColorScheme, ThemeColors] = {
        ColorScheme.DARK: ThemeColors(
            success="green",
            error="red",
            warning="yellow",
            info="blue",
            data="cyan",
            highlight="magenta",
            header="bold blue",
            progress="cyan",
        ),
        ColorScheme.LIGHT: ThemeColors(
            success="green",
            error="red",
            warning="yellow",
            info="blue",
            data="blue",
            highlight="magenta",
            header="bold blue",
            progress="blue",
        ),
    }

    def __init__(
        self,
        color_scheme: ColorScheme = ColorScheme.DARK,
        verbose: bool = False,
    ) -> None:
        """
        Initialize the output interface.

        Args:
            color_scheme: Color scheme to use (dark, light, or auto)
            verbose: Enable verbose logging
        """
        self.color_scheme = color_scheme
        self.verbose = verbose
        self.theme_colors = self._get_theme_colors(color_scheme)

        # Create Rich theme
        rich_theme = Theme(
            {
                "success": self.theme_colors.success,
                "error": self.theme_colors.error,
                "warning": self.theme_colors.warning,
                "info": self.theme_colors.info,
                "data": self.theme_colors.data,
                "highlight": self.theme_colors.highlight,
                "header": self.theme_colors.header,
                "progress": self.theme_colors.progress,
            }
        )

        # Initialize console with theme
        self.console = Console(theme=rich_theme)

        # Install rich traceback
        install_rich_traceback(console=self.console)

        # Setup logging
        self._setup_logging()

    def _get_theme_colors(self, scheme: ColorScheme) -> ThemeColors:
        """Get theme colors based on scheme."""
        if scheme == ColorScheme.AUTO:
            # For now, default to dark. In future, detect system theme
            return self.THEMES[ColorScheme.DARK]
        return self.THEMES[scheme]

    def _setup_logging(self) -> None:
        """Setup logging with Rich handler."""
        level = logging.DEBUG if self.verbose else logging.INFO

        # Remove existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Add rich handler for console
        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
        )
        rich_handler.setLevel(level)

        # Add file handler
        file_handler = logging.FileHandler("muka_analysis.log", mode="w")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # Configure root logger
        root_logger.setLevel(level)
        root_logger.addHandler(rich_handler)
        root_logger.addHandler(file_handler)

    # Output methods

    def print(self, message: str, style: Optional[str] = None) -> None:
        """Print a message with optional styling."""
        self.console.print(message, style=style)

    def success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"✅ {message}", style="success")

    def error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"❌ {message}", style="error")

    def warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"⚠️  {message}", style="warning")

    def info(self, message: str) -> None:
        """Print an informational message."""
        self.console.print(f"ℹ️  {message}", style="info")

    def data(self, message: str) -> None:
        """Print data-related message."""
        self.console.print(message, style="data")

    def header(self, message: str) -> None:
        """Print a header message."""
        self.console.print(f"\n{message}", style="header")

    def separator(self, length: int = 50) -> None:
        """Print a separator line."""
        self.console.print("=" * length, style="info")

    # Table rendering

    def create_table(
        self,
        title: str,
        columns: List[tuple[str, str]],
        show_header: bool = True,
    ) -> Table:
        """
        Create a Rich table with consistent styling.

        Args:
            title: Table title
            columns: List of (column_name, style) tuples
            show_header: Whether to show table header

        Returns:
            Configured Rich Table instance

        Example:
            >>> table = output.create_table(
            ...     "Results",
            ...     [("Metric", "data"), ("Value", "highlight")]
            ... )
            >>> table.add_row("Total", "100")
            >>> output.show_table(table)
        """
        table = Table(
            title=title,
            show_header=show_header,
            header_style=self.theme_colors.header,
        )

        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)

        return table

    def show_table(self, table: Table) -> None:
        """Display a table."""
        self.console.print(table)

    # Progress tracking

    def progress_context(self) -> Progress:
        """
        Create a progress context manager.

        Returns:
            Progress context manager

        Example:
            >>> with output.progress_context() as progress:
            ...     task = progress.add_task("Processing...", total=100)
            ...     for i in range(100):
            ...         progress.update(task, advance=1)
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )

    def simple_progress(self) -> Progress:
        """
        Create a simple progress context without bar.

        Returns:
            Simple progress context manager
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

    # User interaction

    def confirm(self, message: str, default: bool = False) -> bool:
        """
        Prompt user for confirmation.

        Args:
            message: Confirmation message
            default: Default value if user just presses Enter

        Returns:
            True if user confirms, False otherwise

        Example:
            >>> if output.confirm("Delete file?"):
            ...     print("Deleting...")
        """
        return Confirm.ask(message, default=default, console=self.console)

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """
        Prompt user for input.

        Args:
            message: Prompt message
            default: Default value

        Returns:
            User input string
        """
        if default is not None:
            return Prompt.ask(message, default=default, console=self.console)
        return Prompt.ask(message, console=self.console)

    # Summary and reporting

    def show_summary(
        self,
        title: str,
        data: Dict[str, Any],
        highlight_keys: Optional[List[str]] = None,
    ) -> None:
        """
        Display a summary table.

        Args:
            title: Summary title
            data: Dictionary of key-value pairs to display
            highlight_keys: Keys to highlight

        Example:
            >>> output.show_summary(
            ...     "Analysis Results",
            ...     {"Total": 100, "Success": 95, "Failed": 5}
            ... )
        """
        highlight_keys = highlight_keys or []

        table = self.create_table(
            title,
            [("Metric", "data"), ("Value", "highlight")],
        )

        for key, value in data.items():
            style = "highlight" if key in highlight_keys else None
            table.add_row(str(key), str(value), style=style)

        self.show_table(table)

    def show_file_list(
        self,
        title: str,
        files: List[Path],
        style: str = "warning",
    ) -> None:
        """
        Display a list of files.

        Args:
            title: List title
            files: List of file paths
            style: Style to use for files
        """
        self.console.print(f"\n{title}", style="warning")
        for file in files:
            self.console.print(f"   • {file}", style=style)

    # Context managers for sections

    def section(self, title: str) -> None:
        """
        Print a section header.

        Args:
            title: Section title
        """
        self.header(f"🐄 {title}")
        self.separator()


# Global output interface instance (lazy initialization)
_output_interface: Optional[OutputInterface] = None


def get_output() -> OutputInterface:
    """
    Get the global output interface instance.

    Returns:
        OutputInterface instance
    """
    global _output_interface
    if _output_interface is None:
        _output_interface = OutputInterface()
    return _output_interface


def init_output(
    color_scheme: ColorScheme = ColorScheme.DARK,
    verbose: bool = False,
) -> OutputInterface:
    """
    Initialize the global output interface.

    Args:
        color_scheme: Color scheme to use
        verbose: Enable verbose logging

    Returns:
        Initialized OutputInterface instance
    """
    global _output_interface
    _output_interface = OutputInterface(color_scheme=color_scheme, verbose=verbose)
    return _output_interface


__all__ = [
    "OutputInterface",
    "ColorScheme",
    "ThemeColors",
    "get_output",
    "init_output",
]
