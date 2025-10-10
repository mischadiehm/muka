"""
Command Line Interface for MuKa farm classification and analysis.

This module provides a modern CLI using Typer with Rich console output
through an abstracted output interface for consistent styling and theming.
"""

import logging
from collections import Counter
from pathlib import Path
from typing import Annotated, Optional

import typer

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.io_utils import IOUtils
from muka_analysis.output import ColorScheme, init_output

# Create Typer app
app = typer.Typer(
    name="muka-analysis",
    help="MuKa Farm Classification and Analysis Tool",
    add_completion=False,
    rich_markup_mode="rich",
)


@app.command()
def analyze(
    input_file: Annotated[
        Optional[Path],
        typer.Option(
            "--input",
            "-i",
            help="Path to input CSV file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Path to output CSV file for classified farms",
        ),
    ] = None,
    excel_file: Annotated[
        Optional[Path],
        typer.Option(
            "--excel",
            "-x",
            help="Path to output Excel file for analysis summary (only creates if specified)",
        ),
    ] = None,
    save_analysis: Annotated[
        bool,
        typer.Option(
            "--save-analysis",
            help="Save detailed analysis to Excel file (default output/analysis_summary.xlsx)",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing output files without prompting",
        ),
    ] = False,
    show_unclassified_warnings: Annotated[
        bool,
        typer.Option(
            "--show-unclassified-warnings",
            help="Show warnings for farms that could not be classified",
        ),
    ] = False,
    theme: Annotated[
        ColorScheme,
        typer.Option(
            "--theme",
            "-t",
            help="Color scheme: dark, light, or auto",
        ),
    ] = ColorScheme.DARK,
) -> None:
    """
    Analyze and classify farms from CSV data.

    This command runs the complete analysis pipeline:
    - Loads and validates farm data from CSV
    - Classifies farms into groups based on binary indicators
    - Generates summary statistics and analysis
    - Saves classified data and analysis results

    Example:
        [bold]muka-analysis analyze --input data.csv --output results.csv[/bold]
    """
    # Initialize output interface
    output = init_output(color_scheme=theme, verbose=verbose)
    logger = logging.getLogger(__name__)

    # Update configuration with CLI parameter if provided
    from muka_analysis.config import get_config

    config = get_config()
    if show_unclassified_warnings:
        config.classification.show_unclassified_warnings = True

    output.section("MuKa Farm Classification & Analysis")

    try:
        # Set default paths
        if input_file is None:
            input_file = Path("csv/BetriebsFilter_Population_18_09_2025_guy_jr.csv")
        if output_file is None:
            output_file = Path("output/classified_farms.csv")

        # Only set excel_file if save_analysis is True or excel_file is explicitly provided
        if save_analysis and excel_file is None:
            excel_file = Path("output/analysis_summary.xlsx")

        # Check if output files exist and prompt for overwrite
        if not force:
            existing_files = []
            if output_file.exists():
                existing_files.append(output_file)
            if excel_file and excel_file.exists():
                existing_files.append(excel_file)

            if existing_files:
                output.show_file_list(
                    "⚠️  The following files already exist:",
                    existing_files,
                )

                if not output.confirm("\nDo you want to overwrite them?"):
                    output.error("Analysis cancelled.")
                    raise typer.Exit(1)

        # Create output directories
        output_file.parent.mkdir(parents=True, exist_ok=True)
        if excel_file:
            excel_file.parent.mkdir(parents=True, exist_ok=True)

        # Run analysis with progress indicators
        with output.simple_progress() as progress:

            # Load and validate data
            task1 = progress.add_task("Loading and validating data...", total=None)
            logger.info(f"Loading data from: {input_file}")

            if not input_file.exists():
                output.error(f"Input file not found: {input_file}")
                raise typer.Exit(1)

            farms = IOUtils.read_and_parse(input_file)
            progress.update(task1, description="✓ Data loaded and validated")

            # Classify farms
            task2 = progress.add_task("Classifying farms...", total=None)
            classifier = FarmClassifier()
            for farm in farms:
                classifier.classify_farm(farm)
            progress.update(task2, description="✓ Farms classified")

            # Analyze results
            task3 = progress.add_task("Analyzing results...", total=None)
            analyzer = FarmAnalyzer(farms)
            analyzer.get_summary_by_group()  # Generate summary internally
            progress.update(task3, description="✓ Analysis completed")

            # Save results
            task4 = progress.add_task("Saving results...", total=None)
            IOUtils.write_results(farms, output_file)

            # Save analysis to Excel only if requested
            if excel_file:
                analyzer.export_summary_to_excel(str(excel_file))
                logger.info(f"Analysis summary saved to {excel_file}")

            progress.update(task4, description="✓ Results saved")

        # Display summary
        output.success("Analysis completed successfully!")
        output.print("")  # Add spacing

        # Show classification results
        output.section("Classification Results")

        # Count farms by group
        group_counts: Counter[str] = Counter()
        classified_count = 0
        for farm in farms:
            if farm.group:
                if hasattr(farm.group, "value"):
                    group_counts[farm.group.value] += 1
                else:
                    group_counts[str(farm.group)] += 1
                classified_count += 1
            else:
                group_counts["Unclassified"] += 1

        total_farms = len(farms)
        unclassified_count = group_counts.get("Unclassified", 0)

        # Display classification overview
        output.data(f"Total Farms: {total_farms:,}")
        output.data(f"Classified: {classified_count:,} ({classified_count/total_farms*100:.1f}%)")
        output.data(
            f"Unclassified: {unclassified_count:,} ({unclassified_count/total_farms*100:.1f}%)"
        )
        output.print("")

        # Show group distribution table if there are classified farms
        if classified_count > 0:
            output.header("Farm Distribution by Group")

            # Create table for group distribution
            group_table = output.create_table(
                "Groups", [("Group", "header"), ("Count", "data"), ("Percentage", "highlight")]
            )

            for group, count in sorted(group_counts.items()):
                if group != "Unclassified":
                    percentage = (count / classified_count * 100) if classified_count > 0 else 0
                    group_table.add_row(group, f"{count:,}", f"{percentage:.1f}%")

            output.show_table(group_table)
            output.print("")

            # Show summary statistics
            output.header("Summary Statistics by Group")
            summary_df = analyzer.get_summary_by_group()

            if not summary_df.empty:
                # Create table for summary statistics
                stats_table = output.create_table(
                    "Statistics",
                    [
                        ("Group", "header"),
                        ("Count", "data"),
                        ("Avg Animals", "data"),
                        ("Median Animals", "data"),
                        ("Avg Females 3+", "data"),
                        ("Median Females 3+", "data"),
                    ],
                )

                for _, row in summary_df.iterrows():
                    stats_table.add_row(
                        str(row.get("group", "N/A")),
                        f"{int(row.get('count', 0)):,}",
                        f"{row.get('n_animals_total_mean', 0):.1f}",
                        f"{row.get('n_animals_total_median', 0):.1f}",
                        f"{row.get('n_females_age3_total_mean', 0):.1f}",
                        f"{row.get('n_females_age3_total_median', 0):.1f}",
                    )

                output.show_table(stats_table)
                output.print("")
        else:
            output.warning("No farms were successfully classified.")
            output.info(
                "All farms have patterns that don't match any defined classification profile."
            )
            output.print("")

        # Show file outputs
        output.section("Output Files")
        output.data(f"Classified data: {output_file}")
        if excel_file:
            output.data(f"Analysis summary: {excel_file}")
        output.print("")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        output.error(f"Analysis failed: {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Path to CSV file to validate",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging",
        ),
    ] = False,
    theme: Annotated[
        ColorScheme,
        typer.Option(
            "--theme",
            "-t",
            help="Color scheme: dark, light, or auto",
        ),
    ] = ColorScheme.DARK,
) -> None:
    """
    Validate CSV file format and data quality.

    This command performs comprehensive validation of the input CSV file
    without running the full analysis pipeline.

    Example:
        [bold]muka-analysis validate data.csv[/bold]
    """
    # Initialize output interface
    output = init_output(color_scheme=theme, verbose=verbose)
    logger = logging.getLogger(__name__)

    output.section(f"Validating: {input_file}")

    try:
        with output.simple_progress() as progress:

            task = progress.add_task("Validating data...", total=None)

            df = IOUtils.read_csv(input_file, validate=True)

            progress.update(task, description="✓ Validation completed")

        # If we get here, validation passed (IOUtils.read_csv would raise an exception if not)
        output.success("Validation passed!")

        # Show data summary
        summary_data = {
            "Total Rows": len(df),
            "Total Columns": len(df.columns),
            "Missing Values": int(df.isnull().sum().sum()),
        }

        output.show_summary("Data Summary", summary_data)

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        output.error(f"Validation failed: {e}")
        raise typer.Exit(1)


@app.command()
def version(
    theme: Annotated[
        ColorScheme,
        typer.Option(
            "--theme",
            "-t",
            help="Color scheme: dark, light, or auto",
        ),
    ] = ColorScheme.DARK,
) -> None:
    """Show version information."""
    output = init_output(color_scheme=theme, verbose=False)
    output.header("MuKa Analysis Tool")
    output.info("Version: 0.1.0")
    output.info("Python: 3.10+")
    output.info("Frameworks: Pydantic v2, Rich, Typer")


if __name__ == "__main__":
    app()
