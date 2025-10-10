"""
Demo script showing the OutputInterface capabilities.

This script demonstrates all the features of the centralized output interface
including theme switching, logging, progress bars, and table rendering.
"""

import logging
import time
from pathlib import Path

from muka_analysis.output import ColorScheme, init_output

logger = logging.getLogger(__name__)


def demo_basic_output(output) -> None:
    """Demonstrate basic output methods."""
    output.section("Basic Output Methods")

    output.success("This is a success message")
    output.error("This is an error message")
    output.warning("This is a warning message")
    output.info("This is an informational message")
    output.data("This is data-related output")

    output.separator()


def demo_tables(output) -> None:
    """Demonstrate table rendering."""
    output.section("Table Rendering")

    # Custom table
    table = output.create_table(
        "Farm Classification Results",
        [("Group", "data"), ("Count", "highlight"), ("Percentage", "info")],
    )

    table.add_row("Milchvieh", "15,234", "43.6%")
    table.add_row("BKMmZ", "8,521", "24.4%")
    table.add_row("Muku", "6,432", "18.4%")
    table.add_row("BKMoZ", "3,201", "9.2%")
    table.add_row("Unclassified", "1,533", "4.4%")

    output.show_table(table)

    # Summary table
    output.show_summary(
        "Processing Summary",
        {
            "Total Records": 34921,
            "Processed": 34921,
            "Errors": 0,
            "Duration": "2.5 seconds",
        },
        highlight_keys=["Total Records", "Duration"],
    )


def demo_progress(output) -> None:
    """Demonstrate progress indicators."""
    output.section("Progress Indicators")

    # Simple progress without bar
    with output.simple_progress() as progress:
        task = progress.add_task("Loading data...", total=None)
        time.sleep(1)
        progress.update(task, description="✓ Data loaded")

        task = progress.add_task("Classifying farms...", total=None)
        time.sleep(1)
        progress.update(task, description="✓ Farms classified")

        task = progress.add_task("Saving results...", total=None)
        time.sleep(1)
        progress.update(task, description="✓ Results saved")

    output.success("Processing completed!")


def demo_user_interaction(output) -> None:
    """Demonstrate user interaction."""
    output.section("User Interaction")

    # Confirmation
    output.info("Demonstrating confirmation prompt (will not actually wait):")
    output.print("  if output.confirm('Continue with operation?'):")
    output.print("      # Proceed with operation")

    # Input prompt
    output.info("\nDemonstrating input prompt:")
    output.print("  value = output.prompt('Enter threshold:', default='100')")
    output.print("  # Use the value")


def demo_file_display(output) -> None:
    """Demonstrate file list display."""
    output.section("File Display")

    files = [
        Path("output/classified_farms.csv"),
        Path("output/analysis_summary.xlsx"),
        Path("output/validation_report.txt"),
    ]

    output.show_file_list("Output Files", files, style="data")


def demo_logging_integration(output) -> None:
    """Demonstrate logging integration."""
    output.section("Logging Integration")

    output.info("Logging is automatically configured through OutputInterface")

    logger.debug("This is a debug message (visible in verbose mode)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    output.info("All logs are also written to muka_analysis.log")


def main() -> None:
    """Run all demos."""
    print("\n" + "=" * 80)
    print("OutputInterface Demo - Dark Theme")
    print("=" * 80)

    # Demo with dark theme
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    demo_basic_output(output)
    demo_tables(output)
    demo_progress(output)
    demo_user_interaction(output)
    demo_file_display(output)
    demo_logging_integration(output)

    output.separator()
    output.success("Demo completed!")

    # Show theme info
    output.info(f"\nCurrent theme: {output.color_scheme.value}")
    output.info("Try running with --theme light to see the light theme!")


if __name__ == "__main__":
    main()
