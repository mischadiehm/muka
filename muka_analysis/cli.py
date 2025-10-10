"""
Command Line Interface for MuKa farm classification and analysis.

This module provides a modern CLI using Typer with Rich console output
for better user experience and error reporting.
"""

import logging
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table
from rich.traceback import install as install_rich_traceback

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.io_utils import IOUtils

# Install rich traceback handler for better error display
install_rich_traceback()

# Initialize Rich console
console = Console()

# Create Typer app
app = typer.Typer(
    name="muka-analysis",
    help="MuKa Farm Classification and Analysis Tool",
    add_completion=False,
    rich_markup_mode="rich",
)


# Configure rich logging
def setup_logging(verbose: bool = False) -> None:
    """Setup logging with Rich handler for better console output."""
    level = logging.DEBUG if verbose else logging.INFO

    # Remove existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Add rich handler for console
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
    )
    rich_handler.setLevel(level)

    # Add file handler
    file_handler = logging.FileHandler("muka_analysis.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=[rich_handler, file_handler],
        format="%(message)s",
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
            help="Path to output Excel file for analysis summary",
        ),
    ] = None,
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
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    console.print("\n[bold blue]🐄 MuKa Farm Classification & Analysis[/bold blue]")
    console.print("=" * 50)

    try:
        # Set default paths
        if input_file is None:
            input_file = Path("csv/BetriebsFilter_Population_18_09_2025_guy_jr.csv")
        if output_file is None:
            output_file = Path("output/classified_farms.csv")
        if excel_file is None:
            excel_file = Path("output/analysis_summary.xlsx")

        # Check if output files exist and prompt for overwrite
        if not force:
            existing_files = []
            if output_file.exists():
                existing_files.append(str(output_file))
            if excel_file.exists():
                existing_files.append(str(excel_file))

            if existing_files:
                console.print("\n[yellow]⚠️  The following files already exist:[/yellow]")
                for file in existing_files:
                    console.print(f"   • {file}")

                if not Confirm.ask("\nDo you want to overwrite them?"):
                    console.print("[red]Analysis cancelled.[/red]")
                    raise typer.Exit(1)

        # Create output directories
        output_file.parent.mkdir(parents=True, exist_ok=True)
        excel_file.parent.mkdir(parents=True, exist_ok=True)

        # Run analysis with progress indicators
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Load and validate data
            task1 = progress.add_task("Loading and validating data...", total=None)
            logger.info(f"Loading data from: {input_file}")

            if not input_file.exists():
                console.print(f"[red]❌ Input file not found: {input_file}[/red]")
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

            # Save analysis to Excel
            analyzer.export_summary_to_excel(str(excel_file))
            progress.update(task4, description="✓ Results saved")

        # Display summary
        console.print("\n[bold green]✅ Analysis completed successfully![/bold green]")

        # Create summary table
        table = Table(title="Analysis Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Farms", str(len(farms)))
        table.add_row("Input File", str(input_file))
        table.add_row("Output File", str(output_file))
        table.add_row("Excel Report", str(excel_file))

        # Add group counts from farms
        from collections import Counter

        group_counts = Counter()
        for farm in farms:
            if farm.group:
                if hasattr(farm.group, "value"):
                    group_counts[farm.group.value] += 1
                else:
                    group_counts[str(farm.group)] += 1
            else:
                group_counts["Unclassified"] += 1

        for group, count in group_counts.items():
            table.add_row(f"Group {group}", str(count))

        console.print(table)

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        console.print(f"[red]❌ Analysis failed: {e}[/red]")
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
) -> None:
    """
    Validate CSV file format and data quality.

    This command performs comprehensive validation of the input CSV file
    without running the full analysis pipeline.

    Example:
        [bold]muka-analysis validate data.csv[/bold]
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    console.print(f"\n[bold blue]🔍 Validating: {input_file}[/bold blue]")
    console.print("=" * 50)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            task = progress.add_task("Validating data...", total=None)

            df = IOUtils.read_csv(input_file, validate=True)

            progress.update(task, description="✓ Validation completed")

        # If we get here, validation passed (IOUtils.read_csv would raise an exception if not)
        console.print("[bold green]✅ Validation passed![/bold green]")

        # Show data summary
        table = Table(title="Data Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Rows", str(len(df)))
        table.add_row("Total Columns", str(len(df.columns)))
        table.add_row("Missing Values", str(df.isnull().sum().sum()))

        console.print(table)

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold blue]MuKa Analysis Tool[/bold blue]")
    console.print("Version: 0.1.0")
    console.print("Python: 3.10+")


if __name__ == "__main__":
    app()
