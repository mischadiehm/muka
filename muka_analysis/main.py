"""
Main execution script for MuKa farm classification and analysis.

This script orchestrates the entire pipeline:
1. Load and validate data
2. Classify farms into groups
3. Analyze and generate statistics
4. Save results
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.io_utils import IOUtils
from muka_analysis.validation import ValidationSuite, create_validation_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("muka_analysis.log", mode="w"),
    ],
)

logger = logging.getLogger(__name__)


def main(
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
    excel_file: Optional[Path] = None,
) -> None:
    """
    Main execution function for MuKa farm analysis.

    This function runs the complete analysis pipeline:
    1. Reads and validates input data from CSV
    2. Classifies farms into groups based on binary indicators
    3. Generates summary statistics and analysis
    4. Saves classified data and analysis results

    Args:
        input_file: Path to input CSV file. If None, uses default path.
        output_file: Path to output CSV file. If None, uses default path.
        excel_file: Path to output Excel file. If None, uses default path.

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If data validation fails

    Example:
        >>> from pathlib import Path
        >>> main(
        ...     input_file=Path("data/farms.csv"),
        ...     output_file=Path("output/classified_farms.csv"),
        ...     excel_file=Path("output/analysis_summary.xlsx")
        ... )
    """
    logger.info("=" * 70)
    logger.info("Starting MuKa Farm Classification and Analysis")
    logger.info("=" * 70)

    # Set default paths if not provided
    if input_file is None:
        input_file = (
            Path(__file__).parent.parent / "csv" / "BetriebsFilter_Population_18_09_2025_guy_jr.csv"
        )

    if output_file is None:
        output_file = Path(__file__).parent.parent / "output" / "classified_farms.csv"

    if excel_file is None:
        excel_file = Path(__file__).parent.parent / "output" / "analysis_summary.xlsx"

    logger.info(f"Input file: {input_file}")
    logger.info(f"Output CSV: {output_file}")
    logger.info(f"Output Excel: {excel_file}")

    try:
        # Step 1: Load and validate data
        logger.info("\nStep 1: Loading and validating data...")
        farms = IOUtils.read_and_parse(input_file)
        logger.info(f"Successfully loaded {len(farms)} farms")

        # Step 2: Classify farms
        logger.info("\nStep 2: Classifying farms...")
        classifier = FarmClassifier()
        classified_farms = classifier.classify_farms(farms)

        # Count classification results
        classified_count = sum(1 for f in classified_farms if f.group is not None)
        unclassified_count = len(classified_farms) - classified_count
        logger.info(f"Classification complete:")
        logger.info(f"  Classified: {classified_count}")
        logger.info(f"  Unclassified: {unclassified_count}")

        # Step 3: Validate results against reference data
        logger.info("\nStep 3: Validating results against reference data...")
        validation_suite = ValidationSuite()

        # Read the raw dataframe to get the reference 'group' column
        raw_df = IOUtils.read_csv(input_file, validate=False)

        # Analyze reference groups
        reference_groups = validation_suite.analyze_reference_groups(raw_df)
        logger.info("Reference group distribution:")
        for group_name, count in sorted(reference_groups.items()):
            logger.info(f"  {group_name}: {count}")

        # Run validation
        validation_results = validation_suite.run_all_validations(classified_farms, raw_df)

        # Log validation results
        logger.info("\nValidation Results:")
        for result in validation_results:
            logger.info(f"\n{result.message}")

        # Step 4: Analyze results
        logger.info("\nStep 4: Analyzing results...")
        analyzer = FarmAnalyzer(classified_farms)

        # Print summary to console
        analyzer.print_summary()

        # Step 5: Save results
        logger.info("\nStep 5: Saving results...")

        # Save classified farms to CSV
        IOUtils.write_results(classified_farms, output_file)
        logger.info(f"Saved classified farms to: {output_file}")

        # Save analysis summary to Excel (including validation report)
        analyzer.export_summary_to_excel(str(excel_file))
        logger.info(f"Saved analysis summary to: {excel_file}")

        # Add validation report to Excel
        validation_report_df = create_validation_report(validation_results)
        with pd.ExcelWriter(excel_file, mode="a", engine="openpyxl") as writer:
            validation_report_df.to_excel(writer, sheet_name="Validation", index=False)
        logger.info(f"Added validation report to: {excel_file}")

        logger.info("\n" + "=" * 70)
        logger.info("Analysis complete!")
        logger.info("=" * 70)

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Allow command-line arguments for file paths
    import argparse

    parser = argparse.ArgumentParser(description="MuKa Farm Classification and Analysis Tool")
    parser.add_argument("--input", type=Path, help="Path to input CSV file")
    parser.add_argument("--output", type=Path, help="Path to output CSV file")
    parser.add_argument("--excel", type=Path, help="Path to output Excel file")

    args = parser.parse_args()

    main(input_file=args.input, output_file=args.output, excel_file=args.excel)
