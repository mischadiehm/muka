#!/usr/bin/env python3
"""
Demo script showing the centralized configuration system.

This script demonstrates:
1. Loading configuration from defaults, files, and environment
2. Accessing configuration values
3. Using configuration in application code
4. Configuration validation
"""

import logging
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from muka_analysis.config import get_config, init_config, reset_config
from muka_analysis.output import ColorScheme, init_output

logger = logging.getLogger(__name__)


def demo_basic_config():
    """Demonstrate basic configuration loading and access."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Basic Configuration")

    # Get configuration
    config = get_config()

    # Show application info
    output.info(f"Application: {config.app_name} v{config.version}")
    output.info(f"Debug mode: {config.debug}")

    # Show paths
    output.header("Paths Configuration")
    output.data(f"CSV Directory: {config.paths.csv_dir}")
    output.data(f"Output Directory: {config.paths.output_dir}")
    output.data(f"Log File: {config.paths.log_file}")

    # Show default paths
    output.header("Default File Paths")
    output.data(f"Input: {config.paths.get_default_input_path()}")
    output.data(f"Classified Output: {config.paths.get_classified_output_path()}")
    output.data(f"Summary Output: {config.paths.get_summary_output_path()}")


def demo_classification_config():
    """Demonstrate classification configuration."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Classification Configuration")

    config = get_config()

    output.data(f"Presence Threshold: {config.classification.presence_threshold}")
    output.data(f"Require All Fields: {config.classification.require_all_fields}")
    output.data(f"Allow Missing Values: {config.classification.allow_missing_values}")


def demo_analysis_config():
    """Demonstrate analysis configuration."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Analysis Configuration")

    config = get_config()

    output.data(f"Confidence Level: {config.analysis.confidence_level}")
    output.data(f"Percentiles: {config.analysis.percentiles}")
    output.data(f"Min Group Size: {config.analysis.min_group_size}")


def demo_output_config():
    """Demonstrate output configuration."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Output Configuration")

    config = get_config()

    output.data(f"CSV Encoding: {config.output.csv_encoding}")
    output.data(f"CSV Separator: {config.output.csv_separator}")
    output.data(f"Decimal Places: {config.output.decimal_places}")
    output.data(f"Max Display Rows: {config.output.max_display_rows}")
    output.data(f"Show Progress: {config.output.show_progress}")
    output.data(f"Default Theme: {config.output.default_theme}")


def demo_validation_config():
    """Demonstrate validation configuration."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Validation Configuration")

    config = get_config()

    output.data(f"Balance Tolerance: {config.validation.balance_tolerance_pct}%")
    output.data(f"Year Range: {config.validation.min_year} - {config.validation.max_year}")
    output.data(f"Min TVD: {config.validation.min_tvd}")


def demo_logging_config():
    """Demonstrate logging configuration."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Logging Configuration")

    config = get_config()

    output.data(f"Console Level: {config.logging.console_level}")
    output.data(f"File Level: {config.logging.file_level}")
    output.data(f"Show Timestamps: {config.logging.show_timestamps}")
    output.data(f"Show Module Names: {config.logging.show_module_names}")


def demo_config_summary():
    """Demonstrate configuration summary display."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Configuration Summary")

    config = get_config()
    summary = config.summary()

    output.show_summary("Current Configuration", summary)


def demo_env_override():
    """Demonstrate environment variable overrides."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Environment Variable Override")

    # Set some environment variables
    output.info("Setting environment variables:")
    output.data("MUKA_DEBUG=true")
    output.data("MUKA_ANALYSIS__MIN_GROUP_SIZE=50")
    output.data("MUKA_OUTPUT__DEFAULT_THEME=light")

    os.environ["MUKA_DEBUG"] = "true"
    os.environ["MUKA_ANALYSIS__MIN_GROUP_SIZE"] = "50"
    os.environ["MUKA_OUTPUT__DEFAULT_THEME"] = "light"

    # Reset and reload configuration
    reset_config()
    config = init_config(force=True)

    output.info("Configuration after environment override:")
    output.data(f"Debug: {config.debug}")
    output.data(f"Min Group Size: {config.analysis.min_group_size}")
    output.data(f"Default Theme: {config.output.default_theme}")

    # Clean up
    del os.environ["MUKA_DEBUG"]
    del os.environ["MUKA_ANALYSIS__MIN_GROUP_SIZE"]
    del os.environ["MUKA_OUTPUT__DEFAULT_THEME"]
    reset_config()


def demo_config_usage():
    """Demonstrate using configuration in application code."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Using Configuration in Code")

    config = get_config()

    # Example: File processing with config
    output.info("Example: Processing files with configuration")
    output.data(f"Looking for CSV in: {config.paths.csv_dir}")
    output.data(f"Will save output to: {config.paths.output_dir}")

    if config.output.show_progress:
        output.success("Progress bars enabled!")
    else:
        output.warning("Progress bars disabled")

    # Example: Analysis with config
    output.info(f"\nExample: Analysis with min_group_size={config.analysis.min_group_size}")
    output.data(f"Using confidence level: {config.analysis.confidence_level}")
    output.data(f"Calculating percentiles: {config.analysis.percentiles}")

    # Example: Validation with config
    output.info(f"\nExample: Validation with tolerance={config.validation.balance_tolerance_pct}%")
    output.data(f"Accepting years: {config.validation.min_year}-{config.validation.max_year}")


def demo_ensure_directories():
    """Demonstrate automatic directory creation."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.section("Directory Management")

    config = get_config()

    output.info("Ensuring required directories exist...")
    config.ensure_directories()

    # Check if directories exist
    dirs = [config.paths.csv_dir, config.paths.output_dir]
    for directory in dirs:
        if directory.exists():
            output.success(f"✓ {directory} exists")
        else:
            output.error(f"✗ {directory} missing")


def main():
    """Run all configuration demos."""
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

    output.print("\n")
    output.header("🐄 MuKa Configuration System Demo")
    output.separator()
    output.print("\n")

    try:
        # Initialize configuration
        output.info("Initializing configuration system...")
        init_config()
        output.success("Configuration loaded successfully!\n")

        # Run demos
        demo_basic_config()
        output.print("\n")

        demo_classification_config()
        output.print("\n")

        demo_analysis_config()
        output.print("\n")

        demo_output_config()
        output.print("\n")

        demo_validation_config()
        output.print("\n")

        demo_logging_config()
        output.print("\n")

        demo_config_summary()
        output.print("\n")

        demo_config_usage()
        output.print("\n")

        demo_ensure_directories()
        output.print("\n")

        demo_env_override()
        output.print("\n")

        output.separator()
        output.success("✅ All configuration demos completed!")
        output.print("\n")

        output.info("💡 Tips:")
        output.print("  • Copy muka_config.example.toml to muka_config.toml to customize")
        output.print("  • Use MUKA_* environment variables for overrides")
        output.print("  • See CONFIGURATION_GUIDE.md for full documentation")
        output.print("\n")

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        output.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
