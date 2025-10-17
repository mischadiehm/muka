"""
Data filtering functionality for MuKa farm analysis.

This module provides flexible filtering capabilities for farm data including:
- Percentile-based trimming
- Outlier detection (IQR and z-score methods)
- Value range filtering
- Group-based filtering

All filters are composable and return new filtered datasets without modifying
the original data.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np
from pydantic import BaseModel, Field

from muka_analysis.config import get_config
from muka_analysis.models import FarmData, FarmGroup
from muka_analysis.output import OutputInterface, get_output

logger = logging.getLogger(__name__)


class FilterSummary(BaseModel):
    """Summary of applied filters and their effects."""

    filter_name: str = Field(..., description="Name of the filter applied")
    original_count: int = Field(..., description="Number of farms before filter")
    filtered_count: int = Field(..., description="Number of farms after filter")
    removed_count: int = Field(..., description="Number of farms removed")
    removed_percentage: float = Field(..., description="Percentage of farms removed")
    filter_params: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters used for filtering"
    )


class OutlierInfo(BaseModel):
    """Information about detected outliers in a column."""

    column: str = Field(..., description="Column name")
    method: str = Field(..., description="Detection method (iqr/zscore)")
    threshold: float = Field(..., description="Threshold value used")
    outlier_count: int = Field(..., description="Number of outliers detected")
    outlier_percentage: float = Field(..., description="Percentage of outliers")
    lower_bound: Optional[float] = Field(None, description="Lower outlier boundary")
    upper_bound: Optional[float] = Field(None, description="Upper outlier boundary")
    outlier_tvds: List[str] = Field(default_factory=list, description="TVD IDs of outlier farms")


class DataFilter:
    """
    Composable filter for farm data.

    This class provides methods to filter farm datasets based on various criteria.
    All filter operations return a new DataFilter instance, allowing method chaining.

    Example:
        >>> filter = DataFilter(farms)
        >>> filtered = (filter
        ...     .trim_percentile("animalyear_days_female_age3_dairy", 0.10, 0.90)
        ...     .remove_outliers("n_animals_total", method="iqr", threshold=1.5)
        ...     .filter_by_range("year", min_value=2020)
        ... )
        >>> filtered_farms = filtered.get_filtered_farms()
    """

    def __init__(self, farms: List[FarmData], parent_filter: Optional["DataFilter"] = None):
        """
        Initialize filter with farm data.

        Args:
            farms: List of FarmData objects to filter
            parent_filter: Parent filter (for tracking filter chain)
        """
        self.farms = farms
        self.original_count = len(farms) if parent_filter is None else parent_filter.original_count
        self.parent_filter = parent_filter
        self.filter_history: List[FilterSummary] = (
            [] if parent_filter is None else parent_filter.filter_history.copy()
        )
        self.config = get_config()

    def _create_child_filter(
        self, filtered_farms: List[FarmData], filter_summary: FilterSummary
    ) -> "DataFilter":
        """
        Create a new DataFilter instance with filtered farms.

        Args:
            filtered_farms: Filtered list of farms
            filter_summary: Summary of the filter applied

        Returns:
            New DataFilter instance
        """
        child = DataFilter(filtered_farms, parent_filter=self)
        child.filter_history.append(filter_summary)
        return child

    def _get_column_values(self, column: str) -> Tuple[List[float], List[FarmData]]:
        """
        Extract numeric values from farms for a specific column.

        Args:
            column: Column name (attribute of FarmData)

        Returns:
            Tuple of (values, corresponding farms) with non-None values

        Raises:
            ValueError: If column doesn't exist on FarmData
        """
        values = []
        valid_farms = []

        for farm in self.farms:
            if not hasattr(farm, column):
                raise ValueError(
                    f"Column '{column}' does not exist on FarmData. "
                    f"Available columns: {', '.join(dir(farm))}"
                )

            value = getattr(farm, column)
            if value is not None and not (isinstance(value, float) and np.isnan(value)):
                values.append(float(value))
                valid_farms.append(farm)

        if not values:
            logger.warning(f"No valid values found for column '{column}'")

        return values, valid_farms

    def trim_percentile(
        self, column: str, lower_percentile: float = 0.05, upper_percentile: float = 0.95
    ) -> "DataFilter":
        """
        Remove farms in the top and bottom percentiles for a specific column.

        Args:
            column: Column name to filter on
            lower_percentile: Lower percentile threshold (0.0 to 1.0)
            upper_percentile: Upper percentile threshold (0.0 to 1.0)

        Returns:
            New DataFilter with filtered farms

        Raises:
            ValueError: If percentiles are invalid

        Example:
            >>> # Remove bottom 10% and top 10%
            >>> filtered = filter.trim_percentile("animalyear_days_female_age3_dairy", 0.10, 0.90)
        """
        if not 0 <= lower_percentile < upper_percentile <= 1:
            raise ValueError(
                f"Invalid percentiles: lower={lower_percentile}, upper={upper_percentile}. "
                f"Must be 0 <= lower < upper <= 1"
            )

        logger.info(
            f"Trimming {column} to percentile range [{lower_percentile:.2%}, {upper_percentile:.2%}]"
        )

        values, valid_farms = self._get_column_values(column)

        if not values:
            return self  # No valid values, return unchanged

        # Calculate percentile bounds
        lower_value = np.percentile(values, lower_percentile * 100)
        upper_value = np.percentile(values, upper_percentile * 100)

        logger.debug(f"Percentile bounds: [{lower_value:.2f}, {upper_value:.2f}]")

        # Filter farms within bounds
        filtered_farms = [
            farm for farm in valid_farms if lower_value <= getattr(farm, column) <= upper_value
        ]

        # Create summary
        summary = FilterSummary(
            filter_name=f"trim_percentile:{column}",
            original_count=len(self.farms),
            filtered_count=len(filtered_farms),
            removed_count=len(self.farms) - len(filtered_farms),
            removed_percentage=(len(self.farms) - len(filtered_farms)) / len(self.farms) * 100,
            filter_params={
                "column": column,
                "lower_percentile": lower_percentile,
                "upper_percentile": upper_percentile,
                "lower_value": float(lower_value),
                "upper_value": float(upper_value),
            },
        )

        logger.info(
            f"Removed {summary.removed_count} farms ({summary.removed_percentage:.1f}%) "
            f"by percentile trimming"
        )

        return self._create_child_filter(filtered_farms, summary)

    def detect_outliers_iqr(self, column: str, multiplier: Optional[float] = None) -> OutlierInfo:
        """
        Detect outliers using the Interquartile Range (IQR) method.

        Outliers are values that fall outside:
        [Q1 - multiplier * IQR, Q3 + multiplier * IQR]

        Args:
            column: Column name to check for outliers
            multiplier: IQR multiplier (default from config, typically 1.5)

        Returns:
            OutlierInfo with detection results

        Note:
            - multiplier = 1.5: standard outliers (Tukey's method)
            - multiplier = 3.0: extreme outliers only
        """
        if multiplier is None:
            multiplier = self.config.filtering.iqr_multiplier

        logger.info(f"Detecting IQR outliers in {column} (multiplier={multiplier})")

        values, valid_farms = self._get_column_values(column)

        if len(values) < 4:  # Need at least 4 values for quartiles
            logger.warning(f"Insufficient data for IQR outlier detection in {column}")
            return OutlierInfo(
                column=column,
                method="iqr",
                threshold=multiplier,
                outlier_count=0,
                outlier_percentage=0.0,
            )

        # Calculate quartiles and IQR
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        # Calculate bounds
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        logger.debug(
            f"IQR outlier bounds: [{lower_bound:.2f}, {upper_bound:.2f}] "
            f"(Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f})"
        )

        # Identify outliers
        outlier_tvds = []
        outlier_count = 0
        for farm in valid_farms:
            value = getattr(farm, column)
            if value < lower_bound or value > upper_bound:
                outlier_tvds.append(farm.tvd)
                outlier_count += 1

        outlier_pct = (outlier_count / len(valid_farms) * 100) if valid_farms else 0.0

        logger.info(f"Found {outlier_count} IQR outliers ({outlier_pct:.1f}%)")

        return OutlierInfo(
            column=column,
            method="iqr",
            threshold=multiplier,
            outlier_count=outlier_count,
            outlier_percentage=outlier_pct,
            lower_bound=float(lower_bound),
            upper_bound=float(upper_bound),
            outlier_tvds=outlier_tvds,
        )

    def detect_outliers_zscore(self, column: str, threshold: Optional[float] = None) -> OutlierInfo:
        """
        Detect outliers using the Z-score method.

        Outliers are values where |z-score| > threshold.
        z-score = (value - mean) / std_dev

        Args:
            column: Column name to check for outliers
            threshold: Z-score threshold (default from config, typically 3.0)

        Returns:
            OutlierInfo with detection results

        Note:
            - threshold = 3.0: standard (99.7% of normal data)
            - threshold = 2.5: more sensitive
            This method assumes data is approximately normally distributed.
        """
        if threshold is None:
            threshold = self.config.filtering.zscore_threshold

        logger.info(f"Detecting z-score outliers in {column} (threshold={threshold})")

        values, valid_farms = self._get_column_values(column)

        if len(values) < 3:  # Need at least 3 values
            logger.warning(f"Insufficient data for z-score outlier detection in {column}")
            return OutlierInfo(
                column=column,
                method="zscore",
                threshold=threshold,
                outlier_count=0,
                outlier_percentage=0.0,
            )

        # Calculate mean and standard deviation
        mean = np.mean(values)
        std_dev = np.std(values, ddof=1)  # Sample standard deviation

        if std_dev == 0:
            logger.warning(f"Standard deviation is 0 for {column}, no outliers detected")
            return OutlierInfo(
                column=column,
                method="zscore",
                threshold=threshold,
                outlier_count=0,
                outlier_percentage=0.0,
            )

        logger.debug(f"Z-score stats: mean={mean:.2f}, std_dev={std_dev:.2f}")

        # Calculate bounds
        lower_bound = mean - threshold * std_dev
        upper_bound = mean + threshold * std_dev

        # Identify outliers
        outlier_tvds = []
        outlier_count = 0
        for farm in valid_farms:
            value = getattr(farm, column)
            z_score = abs((value - mean) / std_dev)
            if z_score > threshold:
                outlier_tvds.append(farm.tvd)
                outlier_count += 1

        outlier_pct = (outlier_count / len(valid_farms) * 100) if valid_farms else 0.0

        logger.info(f"Found {outlier_count} z-score outliers ({outlier_pct:.1f}%)")

        return OutlierInfo(
            column=column,
            method="zscore",
            threshold=threshold,
            outlier_count=outlier_count,
            outlier_percentage=outlier_pct,
            lower_bound=float(lower_bound),
            upper_bound=float(upper_bound),
            outlier_tvds=outlier_tvds,
        )

    def remove_outliers(
        self, column: str, method: Optional[str] = None, threshold: Optional[float] = None
    ) -> "DataFilter":
        """
        Remove outliers from dataset using specified method.

        Args:
            column: Column name to check for outliers
            method: Detection method ('iqr' or 'zscore'), defaults to config
            threshold: Threshold value (method-specific), defaults to config

        Returns:
            New DataFilter with outliers removed

        Example:
            >>> # Remove IQR outliers with standard threshold
            >>> filtered = filter.remove_outliers("n_animals_total", method="iqr", threshold=1.5)
        """
        if method is None:
            method = self.config.filtering.default_outlier_method

        method = method.lower()
        if method not in ["iqr", "zscore"]:
            raise ValueError(f"Invalid outlier method: {method}. Use 'iqr' or 'zscore'.")

        logger.info(f"Removing {method} outliers from {column}")

        # Detect outliers
        if method == "iqr":
            outlier_info = self.detect_outliers_iqr(column, threshold)
        else:  # zscore
            outlier_info = self.detect_outliers_zscore(column, threshold)

        # Filter out outlier farms
        outlier_tvd_set: Set[str] = set(outlier_info.outlier_tvds)
        filtered_farms = [farm for farm in self.farms if farm.tvd not in outlier_tvd_set]

        # Create summary
        summary = FilterSummary(
            filter_name=f"remove_outliers_{method}:{column}",
            original_count=len(self.farms),
            filtered_count=len(filtered_farms),
            removed_count=len(self.farms) - len(filtered_farms),
            removed_percentage=(len(self.farms) - len(filtered_farms)) / len(self.farms) * 100,
            filter_params={
                "column": column,
                "method": method,
                "threshold": threshold or outlier_info.threshold,
                "lower_bound": outlier_info.lower_bound,
                "upper_bound": outlier_info.upper_bound,
            },
        )

        logger.info(
            f"Removed {summary.removed_count} outlier farms ({summary.removed_percentage:.1f}%)"
        )

        return self._create_child_filter(filtered_farms, summary)

    def filter_by_range(
        self, column: str, min_value: Optional[float] = None, max_value: Optional[float] = None
    ) -> "DataFilter":
        """
        Filter farms by value range for a specific column.

        Args:
            column: Column name to filter on
            min_value: Minimum value (inclusive), None for no lower bound
            max_value: Maximum value (inclusive), None for no upper bound

        Returns:
            New DataFilter with filtered farms

        Example:
            >>> # Keep only farms from years 2020-2024
            >>> filtered = filter.filter_by_range("year", min_value=2020, max_value=2024)
        """
        if min_value is None and max_value is None:
            logger.warning("No range specified, returning unchanged")
            return self

        logger.info(f"Filtering {column} by range: [{min_value}, {max_value}]")

        values, valid_farms = self._get_column_values(column)

        filtered_farms = []
        for farm in valid_farms:
            value = getattr(farm, column)
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                continue
            filtered_farms.append(farm)

        # Create summary
        summary = FilterSummary(
            filter_name=f"range_filter:{column}",
            original_count=len(self.farms),
            filtered_count=len(filtered_farms),
            removed_count=len(self.farms) - len(filtered_farms),
            removed_percentage=(len(self.farms) - len(filtered_farms)) / len(self.farms) * 100,
            filter_params={"column": column, "min_value": min_value, "max_value": max_value},
        )

        logger.info(
            f"Removed {summary.removed_count} farms ({summary.removed_percentage:.1f}%) "
            f"by range filter"
        )

        return self._create_child_filter(filtered_farms, summary)

    def filter_by_group(self, *groups: FarmGroup) -> "DataFilter":
        """
        Filter farms by farm group(s).

        Args:
            *groups: One or more FarmGroup values to keep

        Returns:
            New DataFilter with filtered farms

        Example:
            >>> # Keep only Muku and Milchvieh farms
            >>> filtered = filter.filter_by_group(FarmGroup.MUKU, FarmGroup.MILCHVIEH)
        """
        if not groups:
            logger.warning("No groups specified, returning unchanged")
            return self

        group_names = [g.value for g in groups]
        logger.info(f"Filtering to groups: {group_names}")

        filtered_farms = [farm for farm in self.farms if farm.group in groups]

        # Create summary
        summary = FilterSummary(
            filter_name="group_filter",
            original_count=len(self.farms),
            filtered_count=len(filtered_farms),
            removed_count=len(self.farms) - len(filtered_farms),
            removed_percentage=(len(self.farms) - len(filtered_farms)) / len(self.farms) * 100,
            filter_params={"groups": group_names},
        )

        logger.info(
            f"Removed {summary.removed_count} farms ({summary.removed_percentage:.1f}%) "
            f"by group filter"
        )

        return self._create_child_filter(filtered_farms, summary)

    def exclude_unclassified(self) -> "DataFilter":
        """
        Remove farms that were not classified (group is None).

        Returns:
            New DataFilter with only classified farms

        Example:
            >>> filtered = filter.exclude_unclassified()
        """
        logger.info("Excluding unclassified farms")

        filtered_farms = [farm for farm in self.farms if farm.group is not None]

        # Create summary
        summary = FilterSummary(
            filter_name="exclude_unclassified",
            original_count=len(self.farms),
            filtered_count=len(filtered_farms),
            removed_count=len(self.farms) - len(filtered_farms),
            removed_percentage=(len(self.farms) - len(filtered_farms)) / len(self.farms) * 100,
            filter_params={},
        )

        logger.info(
            f"Removed {summary.removed_count} unclassified farms "
            f"({summary.removed_percentage:.1f}%)"
        )

        return self._create_child_filter(filtered_farms, summary)

    def filter_custom(self, filter_func: Callable[[FarmData], bool], name: str) -> "DataFilter":
        """
        Apply a custom filter function.

        Args:
            filter_func: Function that takes FarmData and returns True to keep
            name: Name for this filter (for logging and summary)

        Returns:
            New DataFilter with filtered farms

        Example:
            >>> # Keep only farms with more than 50 animals in 2023
            >>> filtered = filter.filter_custom(
            ...     lambda farm: farm.n_animals_total > 50 and farm.year == 2023,
            ...     "large_farms_2023"
            ... )
        """
        logger.info(f"Applying custom filter: {name}")

        filtered_farms = [farm for farm in self.farms if filter_func(farm)]

        # Create summary
        summary = FilterSummary(
            filter_name=f"custom:{name}",
            original_count=len(self.farms),
            filtered_count=len(filtered_farms),
            removed_count=len(self.farms) - len(filtered_farms),
            removed_percentage=(len(self.farms) - len(filtered_farms)) / len(self.farms) * 100,
            filter_params={"name": name},
        )

        logger.info(
            f"Removed {summary.removed_count} farms ({summary.removed_percentage:.1f}%) "
            f"by custom filter"
        )

        return self._create_child_filter(filtered_farms, summary)

    def get_filtered_farms(self) -> List[FarmData]:
        """
        Get the current filtered list of farms.

        Returns:
            List of FarmData objects after all filters applied
        """
        return self.farms

    def get_filter_summary(self) -> List[FilterSummary]:
        """
        Get summary of all filters applied in the chain.

        Returns:
            List of FilterSummary objects
        """
        return self.filter_history

    def print_filter_summary(self, output: Optional[OutputInterface] = None) -> None:
        """
        Print a formatted summary of all applied filters.

        Args:
            output: OutputInterface for display (uses default if None)
        """
        if output is None:
            output = get_output()

        if not self.filter_history:
            output.info("No filters applied")
            return

        output.section("Filter Summary")
        output.info(f"Original farms: {self.original_count:,}")
        output.info(f"Filtered farms: {len(self.farms):,}")
        output.info(
            f"Total removed: {self.original_count - len(self.farms):,} "
            f"({(self.original_count - len(self.farms)) / self.original_count * 100:.1f}%)"
        )
        output.print("")

        # Show each filter
        for i, summary in enumerate(self.filter_history, 1):
            output.header(f"Filter {i}: {summary.filter_name}")
            output.data(f"  Farms before: {summary.original_count:,}")
            output.data(f"  Farms after:  {summary.filtered_count:,}")
            output.data(
                f"  Removed:      {summary.removed_count:,} ({summary.removed_percentage:.1f}%)"
            )
            if summary.filter_params:
                output.data("  Parameters:")
                for key, value in summary.filter_params.items():
                    output.data(f"    {key}: {value}")
            output.print("")

        # Warn if too many farms removed
        total_removed_pct = (self.original_count - len(self.farms)) / self.original_count
        if total_removed_pct > self.config.filtering.warn_if_removed_pct:
            output.warning(
                f"Warning: {total_removed_pct:.1%} of farms removed by filtering. "
                f"Consider reviewing filter parameters."
            )

        # Warn if too few farms remaining
        if len(self.farms) < self.config.filtering.min_farms_after_filter:
            output.error(
                f"Error: Only {len(self.farms)} farms remaining after filtering. "
                f"Minimum required: {self.config.filtering.min_farms_after_filter}"
            )
