"""
Statistical analysis framework for farm data.

This module provides statistical analysis capabilities including:
- Distribution analysis (mean, std, percentiles, skewness, kurtosis)
- Outlier detection and reporting
- Console-based data visualizations

Completely separate from the classification analyzer.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import numpy as np
import pandas as pd

from muka_analysis.models import FarmData

if TYPE_CHECKING:
    from muka_analysis.filters import OutlierInfo
    from muka_analysis.output import OutputInterface

logger = logging.getLogger(__name__)

# Cache scipy import to avoid repeated import attempts
_scipy_stats = None
_scipy_available = None


def _get_scipy_stats() -> Optional[Any]:
    """Get scipy.stats module if available, cached."""
    global _scipy_stats, _scipy_available

    if _scipy_available is None:
        try:
            from scipy import stats as scipy_stats

            _scipy_stats = scipy_stats
            _scipy_available = True
            logger.debug("scipy available for advanced statistics")
        except ImportError:
            _scipy_available = False
            logger.debug("scipy not available, skipping skewness/kurtosis")

    return _scipy_stats if _scipy_available else None


class StatisticalAnalyzer:
    """
    Statistical analyzer for farm data.

    Provides distribution analysis, outlier detection, and visualizations
    without mixing classification logic. Can work with any farm data,
    classified or unclassified.
    """

    def __init__(self, farms: List[FarmData]) -> None:
        """
        Initialize statistical analyzer with farm data.

        Args:
            farms: List of FarmData objects (can be classified or not)

        Raises:
            ValueError: If farms list is empty
        """
        if not farms:
            raise ValueError("Cannot initialize analyzer with empty farms list")

        self.farms = farms
        self.df = self._create_dataframe()
        logger.info(f"Statistical analyzer initialized with {len(farms)} farms")

    def _create_dataframe(self) -> pd.DataFrame:
        """
        Create pandas DataFrame from farm data for statistical operations.

        Returns:
            DataFrame with all farm fields
        """
        data = []
        for farm in self.farms:
            farm_dict = farm.model_dump()
            # Include group if farm is classified
            farm_dict["group"] = farm.group.value if farm.group else None
            data.append(farm_dict)

        return pd.DataFrame(data)

    def analyze_outliers(
        self, columns: List[str], method: str = "iqr", threshold: Optional[float] = None
    ) -> Dict[str, "OutlierInfo"]:
        """
        Analyze outliers for multiple columns.

        Args:
            columns: List of column names to analyze
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold value (method-specific)

        Returns:
            Dictionary mapping column names to OutlierInfo objects

        Example:
            >>> analyzer = StatisticalAnalyzer(farms)
            >>> report = analyzer.analyze_outliers(
            ...     columns=["animalyear_days_female_age3_dairy", "n_animals_total"],
            ...     method="iqr",
            ...     threshold=1.5
            ... )
        """
        from muka_analysis.config import get_config
        from muka_analysis.filters import DataFilter

        config = get_config()

        # GUARD RAIL: Limit number of columns to prevent excessive processing
        if len(columns) > config.filtering.max_outlier_columns_batch:
            logger.warning(
                f"Analyzing {len(columns)} columns exceeds limit of "
                f"{config.filtering.max_outlier_columns_batch}. "
                f"Processing first {config.filtering.max_outlier_columns_batch} columns only."
            )
            columns = columns[: config.filtering.max_outlier_columns_batch]

        logger.info(f"Analyzing outliers for {len(columns)} columns using {method} method")

        filter_obj = DataFilter(self.farms)
        results = {}

        for column in columns:
            try:
                if method.lower() == "iqr":
                    results[column] = filter_obj.detect_outliers_iqr(column, threshold)
                elif method.lower() == "zscore":
                    results[column] = filter_obj.detect_outliers_zscore(column, threshold)
                else:
                    logger.error(f"Invalid outlier method: {method}")
                    raise ValueError(f"Invalid method: {method}. Use 'iqr' or 'zscore'")
            except Exception as e:
                logger.error(f"Error analyzing outliers for {column}: {e}")
                # Continue with other columns

        return results

    def get_distribution_summary(self, column: str, by_group: bool = False) -> pd.DataFrame:
        """
        Get detailed distribution summary for a column.

        Args:
            column: Column name to analyze
            by_group: If True, calculate distribution separately for each group

        Returns:
            DataFrame with distribution statistics

        Example:
            >>> analyzer = StatisticalAnalyzer(farms)
            >>> dist = analyzer.get_distribution_summary("animalyear_days_female_age3_dairy")
        """
        from muka_analysis.config import get_config

        config = get_config()

        # GUARD RAIL: Check dataset size for by_group operations
        if by_group and len(self.farms) > config.filtering.max_farms_for_distribution_by_group:
            logger.warning(
                f"Dataset has {len(self.farms):,} farms, exceeding limit of "
                f"{config.filtering.max_farms_for_distribution_by_group:,} for by_group analysis. "
                f"Running overall distribution only."
            )
            by_group = False

        if not by_group:
            # Overall distribution
            values = self.df[column].dropna()

            if len(values) == 0:
                logger.warning(f"No valid values found for {column}")
                return pd.DataFrame()

            stats = {
                "group": "All",
                "count": len(values),
                "mean": values.mean(),
                "std": values.std(),
                "min": values.min(),
                "max": values.max(),
            }

            # Add percentiles
            for p in config.visualization.show_percentiles:
                stats[f"p{int(p*100)}"] = values.quantile(p)

            # Add skewness and kurtosis if scipy available
            scipy_stats = _get_scipy_stats()
            if scipy_stats is not None:
                stats["skewness"] = scipy_stats.skew(values)
                stats["kurtosis"] = scipy_stats.kurtosis(values)

            return pd.DataFrame([stats])

        else:
            # Distribution by group
            classified_df = self.df[self.df["group"].notna()].copy()

            if classified_df.empty:
                logger.warning("No classified farms found")
                return pd.DataFrame()

            all_stats = []

            for group_name, group_df in classified_df.groupby("group"):
                values = group_df[column].dropna()

                if len(values) == 0:
                    continue

                stats = {
                    "group": group_name,
                    "count": len(values),
                    "mean": values.mean(),
                    "std": values.std(),
                    "min": values.min(),
                    "max": values.max(),
                }

                # Add percentiles
                for p in config.visualization.show_percentiles:
                    stats[f"p{int(p*100)}"] = values.quantile(p)

                # Add skewness and kurtosis if scipy available
                scipy_stats = _get_scipy_stats()
                if scipy_stats is not None:
                    stats["skewness"] = scipy_stats.skew(values)
                    stats["kurtosis"] = scipy_stats.kurtosis(values)

                all_stats.append(stats)

            return pd.DataFrame(all_stats)

    def display_distribution_summary(
        self,
        column: str,
        by_group: bool = False,
        output: Optional["OutputInterface"] = None,
    ) -> None:
        """
        Display distribution summary with Rich formatting.

        Args:
            column: Column name to analyze
            by_group: If True, show distribution by group
            output: OutputInterface for display (uses default if None)
        """
        from rich.table import Table

        from muka_analysis.output import get_output

        if output is None:
            output = get_output()

        output.section(f"Distribution Summary: {column}")

        dist_df = self.get_distribution_summary(column, by_group=by_group)

        if dist_df.empty:
            output.warning(f"No data available for {column}")
            return

        # Create Rich table
        table = Table(show_header=True, header_style="bold cyan")
        for col in dist_df.columns:
            table.add_column(col)

        for _, row in dist_df.iterrows():
            formatted_row = []
            for col in dist_df.columns:
                val = row[col]
                if col == "group":
                    formatted_row.append(str(val))
                elif col == "count":
                    formatted_row.append(f"{int(val):,}")
                else:
                    formatted_row.append(f"{float(val):.2f}")
            table.add_row(*formatted_row)

        output.console.print(table)

    def display_outlier_report(
        self, outlier_report: Dict[str, "OutlierInfo"], output: Optional["OutputInterface"] = None
    ) -> None:
        """
        Display outlier analysis report with visualizations.

        Args:
            outlier_report: Dictionary of column name to OutlierInfo
            output: OutputInterface for display (uses default if None)
        """
        from rich.table import Table

        from muka_analysis.output import get_output

        if output is None:
            output = get_output()

        output.section("Outlier Analysis Report")

        for column, info in outlier_report.items():
            output.header(f"Column: {column}")

            # Create summary table
            table = Table(show_header=False, box=None)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Detection Method", info.method.upper())
            table.add_row("Threshold", f"{info.threshold:.2f}")
            table.add_row("Outliers Found", f"{info.outlier_count:,}")
            table.add_row("Outlier Percentage", f"{info.outlier_percentage:.1f}%")

            if info.lower_bound is not None:
                table.add_row("Lower Bound", f"{info.lower_bound:.2f}")
            if info.upper_bound is not None:
                table.add_row("Upper Bound", f"{info.upper_bound:.2f}")

            output.console.print(table)

            # Show sample of outlier TVDs if any
            if info.outlier_tvds and len(info.outlier_tvds) > 0:
                output.print("")
                sample_size = min(10, len(info.outlier_tvds))
                output.data(f"Sample outlier TVDs (showing {sample_size}):")
                for tvd in info.outlier_tvds[:sample_size]:
                    output.data(f"  • {tvd}")
                if len(info.outlier_tvds) > sample_size:
                    output.data(f"  ... and {len(info.outlier_tvds) - sample_size} more")

            output.print("")

    def create_console_histogram(
        self,
        column: str,
        by_group: bool = False,
        highlight_outliers: bool = False,
        method: str = "iqr",
        threshold: Optional[float] = None,
    ) -> None:
        """
        Create and display a simple ASCII histogram in the console.

        Args:
            column: Column name to visualize
            by_group: If True, create separate histograms for each group
            highlight_outliers: If True, mark outliers in the histogram
            method: Outlier detection method if highlight_outliers is True
            threshold: Outlier threshold if highlight_outliers is True
        """
        from muka_analysis.config import get_config
        from muka_analysis.output import get_output

        output = get_output()
        config = get_config()

        if not by_group:
            values = self.df[column].dropna().values

            if len(values) == 0:
                output.warning(f"No data for {column}")
                return

            self._display_histogram(column, values, "All Farms", output, config)
        else:
            classified_df = self.df[self.df["group"].notna()].copy()

            # GUARD RAIL: Limit number of groups for histograms
            num_groups = classified_df["group"].nunique()
            if num_groups > config.filtering.max_histogram_groups:
                output.warning(
                    f"Dataset has {num_groups} groups, exceeding limit of "
                    f"{config.filtering.max_histogram_groups} for histogram display. "
                    f"Showing overall histogram only."
                )
                values = self.df[column].dropna().values
                if len(values) > 0:
                    self._display_histogram(column, values, "All Farms", output, config)
                return

            for group_name, group_df in classified_df.groupby("group"):
                values = group_df[column].dropna().values

                if len(values) == 0:
                    continue

                self._display_histogram(column, values, group_name, output, config)

    def _display_histogram(
        self, column: str, values: Any, group_name: str, output: Any, config: Any
    ) -> None:
        """Helper method to display a single histogram."""
        output.header(f"{group_name}: {column}")

        # PERFORMANCE: Use numpy.histogram instead of pandas.cut (3-5x faster)
        hist_counts, bin_edges = np.histogram(values, bins=config.visualization.histogram_bins)

        max_count = hist_counts.max() if len(hist_counts) > 0 else 0
        width = config.visualization.histogram_width - 20  # Reserve space for labels

        output.print("")
        output.data(
            f"Count: {len(values):,}  Min: {values.min():.2f}  Max: {values.max():.2f}  Mean: {values.mean():.2f}"
        )
        output.print("")

        # Draw histogram
        for i, count in enumerate(hist_counts):
            bar_length = int((count / max_count) * width) if max_count > 0 else 0
            bar = "█" * bar_length
            bin_start = bin_edges[i]
            bin_end = bin_edges[i + 1]
            label = f"{bin_start:8.1f} - {bin_end:8.1f}"
            output.console.print(f"{label} │{bar} {count}")

        output.print("")
