"""
Main execution script for MuKa farm classification and analysis.

This script now uses the modern CLI interface with Typer and Rich.
For direct usage, use the CLI: uv run python -m muka_analysis.cli
"""

import logging
from pathlib import Path
from typing import Optional

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.io_utils import IOUtils

logger = logging.getLogger(__name__)


def main(
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
    excel_file: Optional[Path] = None,
) -> None:
    """
    Main execution function for MuKa farm analysis.

    This is a legacy function maintained for backward compatibility.
    For modern CLI usage, use: uv run python -m muka_analysis.cli

    Args:
        input_file: Path to input CSV file. If None, uses default path.
        output_file: Path to output CSV file. If None, uses default path.
        excel_file: Path to output Excel file. If None, uses default path.

    Example:
        >>> from pathlib import Path
        >>> main(
        ...     input_file=Path("data/farms.csv"),
        ...     output_file=Path("output/classified_farms.csv"),
        ...     excel_file=Path("output/analysis_summary.xlsx")
        ... )
    """
    # Configure basic logging for legacy mode
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Running legacy analysis function")
    logger.warning("Consider using the modern CLI: uv run python -m muka_analysis.cli analyze")

    # Set default file paths if not provided
    if input_file is None:
        input_file = Path("csv/BetriebsFilter_Population_18_09_2025_guy_jr.csv")
    if output_file is None:
        output_file = Path("output/classified_farms.csv")
    if excel_file is None:
        excel_file = Path("output/analysis_summary.xlsx")

    try:
        logger.info(f"Input file: {input_file}")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Excel file: {excel_file}")

        # Load and parse data
        logger.info("Loading and parsing farm data...")
        farms = IOUtils.read_and_parse(input_file)
        logger.info(f"Loaded {len(farms)} farms")

        # Classify farms
        logger.info("Classifying farms...")
        classifier = FarmClassifier()
        for farm in farms:
            classifier.classify_farm(farm)

        # Generate analysis
        logger.info("Analyzing results...")
        analyzer = FarmAnalyzer(farms)

        # Create output directories
        output_file.parent.mkdir(parents=True, exist_ok=True)
        excel_file.parent.mkdir(parents=True, exist_ok=True)

        # Save results
        logger.info("Saving results...")
        IOUtils.write_results(farms, output_file)
        analyzer.export_summary_to_excel(str(excel_file))

        # Print summary
        analyzer.print_summary()

        logger.info("Analysis completed successfully!")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Import and run the modern CLI instead
    try:
        from muka_analysis.cli import app

        app()
    except ImportError as e:
        logger.warning(f"Modern CLI not available ({e}), running legacy version")
        import argparse

        parser = argparse.ArgumentParser(description="MuKa Farm Classification and Analysis Tool")
        parser.add_argument("--input", type=Path, help="Path to input CSV file")
        parser.add_argument("--output", type=Path, help="Path to output CSV file")
        parser.add_argument("--excel", type=Path, help="Path to output Excel file")

        args = parser.parse_args()
        main(input_file=args.input, output_file=args.output, excel_file=args.excel)
