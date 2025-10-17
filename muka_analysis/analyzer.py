"""
Classification analysis for MuKa farm data.

This module provides functions to analyze CLASSIFIED farm data and
generate summary statistics by farm group.

For statistical analysis (distributions, outliers, visualizations),
use muka_analysis.statistics.StatisticalAnalyzer instead.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from muka_analysis.models import FarmData, FarmGroup

logger = logging.getLogger(__name__)


class FarmAnalyzer:
    """
    Analyzer for generating statistics and summaries of classified farm data.

    This class provides methods to calculate descriptive statistics for farm
    groups and generate summary tables.
    """

    NUMERIC_FIELDS: List[str] = [
        "n_animals_total",
        "n_females_age3_dairy",
        "n_days_female_age3_dairy",
        "n_days_female_age3_double",
        "n_days_female_age3_dairydouble_V2",
        "animalyear_days_female_age3_dairy",
        "animalyear_days_female_age3_double",
        "animalyear_days_female_age3_dairydouble_V2",
        "prop_days_female_age3_dairy",
        "n_females_age3_total",
        "n_total_entries_younger85",
        "n_total_leavings_younger51",
        "n_females_younger731",
        "prop_females_slaughterings_younger731",
        "n_animals_from51_to730",
    ]

    CLASSIFICATION_FIELDS: List[str] = [
        "indicator_female_dairy_cattle_v2",
        "indicator_female_cattle",
        "indicator_calf_arrivals",
        "indicator_calf_leavings",
        "indicator_female_slaughterings",
        "indicator_young_slaughterings",
    ]

    def __init__(self, farms: List[FarmData]) -> None:
        """
        Initialize analyzer with farm data.

        Args:
            farms: List of classified FarmData objects

        Raises:
            ValueError: If farms list is empty
        """
        if not farms:
            raise ValueError("Cannot initialize analyzer with empty farms list")

        self.farms = farms
        self.df = self._create_dataframe()
        logger.info(f"Analyzer initialized with {len(farms)} farms")

    def _create_dataframe(self) -> pd.DataFrame:
        """
        Create a pandas DataFrame from farm data for analysis.

        Returns:
            DataFrame with all farm data including classification indicators
        """
        data = []
        for farm in self.farms:
            data.append(
                {
                    "tvd": farm.tvd,
                    "year": farm.year,
                    # Classification indicators (for grouping in analysis)
                    "indicator_female_dairy_cattle_v2": farm.indicator_female_dairy_cattle_v2,
                    "indicator_female_cattle": farm.indicator_female_cattle,
                    "indicator_calf_arrivals": farm.indicator_calf_arrivals,
                    "indicator_calf_leavings": farm.indicator_calf_leavings,
                    "indicator_female_slaughterings": farm.indicator_female_slaughterings,
                    "indicator_young_slaughterings": farm.indicator_young_slaughterings,
                    # Assigned group from classification
                    "group": (
                        farm.group.value
                        if farm.group and hasattr(farm.group, "value")
                        else farm.group
                    ),
                    # Numeric fields for statistical analysis
                    "n_animals_total": farm.n_animals_total,
                    "n_females_age3_dairy": farm.n_females_age3_dairy,
                    "n_days_female_age3_dairy": farm.n_days_female_age3_dairy,
                    "n_days_female_age3_double": farm.n_days_female_age3_double,
                    "n_days_female_age3_dairydouble_V2": farm.n_days_female_age3_dairydouble_V2,
                    "animalyear_days_female_age3_dairy": farm.animalyear_days_female_age3_dairy,
                    "animalyear_days_female_age3_double": farm.animalyear_days_female_age3_double,
                    "animalyear_days_female_age3_dairydouble_V2": farm.animalyear_days_female_age3_dairydouble_V2,
                    "prop_days_female_age3_dairy": farm.prop_days_female_age3_dairy,
                    "n_females_age3_total": farm.n_females_age3_total,
                    "n_total_entries_younger85": farm.n_total_entries_younger85,
                    "n_total_leavings_younger51": farm.n_total_leavings_younger51,
                    "n_females_younger731": farm.n_females_younger731,
                    "prop_females_slaughterings_younger731": farm.prop_females_slaughterings_younger731,
                    "n_animals_from51_to730": farm.n_animals_from51_to730,
                }
            )

        return pd.DataFrame(data)

    def get_group_counts(self) -> Dict[str, int]:
        """
        Get count of farms in each group.

        Returns:
            Dictionary mapping group names to farm counts

        Example:
            >>> analyzer = FarmAnalyzer(farms)
            >>> counts = analyzer.get_group_counts()
            >>> print(counts)
            {'Muku': 150, 'Milchvieh': 300, ...}
        """
        # Filter out None values
        classified_df = self.df[self.df["group"].notna()]
        counts = classified_df["group"].value_counts().to_dict()

        # Add unclassified count
        unclassified_count = self.df["group"].isna().sum()
        if unclassified_count > 0:
            counts["Unclassified"] = unclassified_count

        # Convert numpy types to native Python int for proper serialization
        counts = {k: int(v) for k, v in counts.items()}

        logger.info(f"Group counts: {counts}")
        return counts

    def calculate_group_statistics(self, group: Optional[FarmGroup] = None) -> pd.DataFrame:
        """
        Calculate descriptive statistics for numeric fields grouped by assigned farm group.

        This uses the 'group' column which contains the classification result
        (Muku, Muku_Amme, Milchvieh, BKMmZ, BKMoZ, IKM).

        Args:
            group: Specific group to analyze, or None for all groups

        Returns:
            DataFrame with statistics (min, max, mean, median) for each farm group

        Note:
            Statistics are calculated for all numeric fields defined in NUMERIC_FIELDS.
            Only farms with an assigned group (not None/Unclassified) are included.
        """
        # Filter out unclassified farms (group is None)
        classified_df = self.df[self.df["group"].notna()].copy()

        if classified_df.empty:
            logger.warning("No classified farms found")
            return pd.DataFrame()

        if group is not None:
            # For specific group, filter by group value
            group_df = classified_df[classified_df["group"] == group.value]
            if group_df.empty:
                logger.warning(f"No farms found in group {group.value}")
                return pd.DataFrame()
            dfs_to_analyze = {group.value: group_df}
        else:
            # Group by the 'group' column (assigned classification)
            dfs_to_analyze = {}
            for group_name, group_df in classified_df.groupby("group"):
                dfs_to_analyze[group_name] = group_df

        all_stats = []

        for group_name, group_df in dfs_to_analyze.items():
            stats_dict = {"group": group_name, "count": len(group_df)}

            for field in self.NUMERIC_FIELDS:
                if field in group_df.columns:
                    values = group_df[field]
                    stats_dict[f"{field}_min"] = values.min()
                    stats_dict[f"{field}_max"] = values.max()
                    stats_dict[f"{field}_mean"] = values.mean()
                    stats_dict[f"{field}_median"] = values.median()

            all_stats.append(stats_dict)

        stats_df = pd.DataFrame(all_stats)

        # Sort by group name for consistent ordering
        if not stats_df.empty and "group" in stats_df.columns:
            # Define desired group order
            group_order = ["Muku", "Muku_Amme", "Milchvieh", "BKMmZ", "BKMoZ", "IKM"]
            stats_df["group"] = pd.Categorical(
                stats_df["group"], categories=group_order, ordered=True
            )
            stats_df = stats_df.sort_values("group").reset_index(drop=True)

        logger.info(f"Calculated statistics for {len(all_stats)} groups")

        return stats_df

    def get_summary_by_group(self) -> pd.DataFrame:
        """
        Get a summary table with key metrics grouped by farm group.

        Returns:
            DataFrame with summary statistics for each farm group

        Note:
            This provides a condensed view with the most important metrics.
            Only includes classified farms (excludes Unclassified).
        """
        summary_stats = self.calculate_group_statistics()

        # Select key columns for summary
        key_columns = [
            "group",
            "count",
            "n_animals_total_mean",
            "n_animals_total_median",
            "animalyear_days_female_age3_dairy_mean",
            "animalyear_days_female_age3_dairy_median",
            "animalyear_days_female_age3_double_mean",
            "animalyear_days_female_age3_double_median",
            "animalyear_days_female_age3_dairydouble_V2_mean",
            "animalyear_days_female_age3_dairydouble_V2_median",
            "n_total_entries_younger85_mean",
            "n_total_leavings_younger51_mean",
        ]

        available_columns = [col for col in key_columns if col in summary_stats.columns]
        summary = summary_stats[available_columns].copy()

        # Round numeric columns
        numeric_cols = summary.select_dtypes(include=["float64"]).columns
        summary[numeric_cols] = summary[numeric_cols].round(2)

        return summary

    def get_farms_by_group(self, group: FarmGroup) -> List[FarmData]:
        """
        Get all farms belonging to a specific group.

        Args:
            group: FarmGroup to filter by

        Returns:
            List of FarmData objects in the specified group
        """
        return [farm for farm in self.farms if farm.group == group]

    def get_unclassified_farms(self) -> List[FarmData]:
        """
        Get all farms that could not be classified.

        Returns:
            List of FarmData objects with group=None
        """
        return [farm for farm in self.farms if farm.group is None]

    def export_summary_to_excel(self, file_path: str, mode_name: Optional[str] = None) -> None:
        """
        Export analysis summary to an Excel file with multiple sheets.

        Args:
            file_path: Path to output Excel file
            mode_name: Optional indicator mode name for sheet naming (e.g., "6-indicators-flex")

        Note:
            Sheets included:
            - Summary[_{mode}]: Overview statistics by farm group
            - Detailed_Stats[_{mode}]: Full statistics for all metrics by farm group
            - Group_Counts[_{mode}]: Counts of farms in each group
        """
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Use mode-specific names if provided
            summary_sheet = f"Summary_{mode_name}" if mode_name else "Summary"
            detailed_sheet = f"Detailed_Stats_{mode_name}" if mode_name else "Detailed_Stats"
            counts_sheet = f"Group_Counts_{mode_name}" if mode_name else "Group_Counts"

            # Summary sheet - based on assigned groups
            summary = self.get_summary_by_group()
            summary.to_excel(writer, sheet_name=summary_sheet, index=False)

            # Detailed statistics sheet - based on assigned groups
            detailed_stats = self.calculate_group_statistics()
            detailed_stats.to_excel(writer, sheet_name=detailed_sheet, index=False)

            # Group counts
            counts = self.get_group_counts()
            counts_df = pd.DataFrame(list(counts.items()), columns=["Group", "Count"])
            # Sort by group name
            group_order = [
                "Muku",
                "Muku_Amme",
                "Milchvieh",
                "BKMmZ",
                "BKMoZ",
                "IKM",
                "Unclassified",
            ]
            counts_df["Group"] = pd.Categorical(
                counts_df["Group"], categories=group_order, ordered=True
            )
            counts_df = counts_df.sort_values("Group").reset_index(drop=True)
            counts_df.to_excel(writer, sheet_name=counts_sheet, index=False)

        mode_info = f" with mode {mode_name}" if mode_name else ""
        logger.info(f"Exported analysis summary to {file_path}{mode_info}")

    def export_with_mode_name(
        self, file_path: str, mode_name: str, include_detailed_stats: bool = True
    ) -> None:
        """
        Export analysis summary to Excel with mode-specific sheet names.

        Args:
            file_path: Path to output Excel file
            mode_name: Indicator mode name for sheet naming
            include_detailed_stats: Whether to include detailed statistics sheet

        Note:
            Sheets included:
            - Summary_{mode}: Overview statistics by farm group
            - Detailed_Stats_{mode}: Full statistics for all metrics (if enabled)
            - Group_Counts_{mode}: Counts of farms in each group
        """
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Summary sheet with mode suffix
            summary = self.get_summary_by_group()
            sheet_name = f"Summary_{mode_name}"
            summary.to_excel(writer, sheet_name=sheet_name, index=False)

            # Detailed statistics sheet with mode suffix (if enabled)
            if include_detailed_stats:
                detailed_stats = self.calculate_group_statistics()
                sheet_name = f"Detailed_Stats_{mode_name}"
                detailed_stats.to_excel(writer, sheet_name=sheet_name, index=False)

            # Group counts with mode suffix
            counts = self.get_group_counts()
            counts_df = pd.DataFrame(list(counts.items()), columns=["Group", "Count"])
            # Sort by group name
            group_order = [
                "Muku",
                "Muku_Amme",
                "Milchvieh",
                "BKMmZ",
                "BKMoZ",
                "IKM",
                "Unclassified",
            ]
            counts_df["Group"] = pd.Categorical(
                counts_df["Group"], categories=group_order, ordered=True
            )
            counts_df = counts_df.sort_values("Group").reset_index(drop=True)
            sheet_name = f"Group_Counts_{mode_name}"
            counts_df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"Exported mode-specific analysis to {file_path}")

    @staticmethod
    def create_comparison_summary(mode_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a comprehensive comparison summary across multiple indicator modes.

        Args:
            mode_results: Dictionary mapping mode names to their analysis results.
                Each result dict should contain: 'total_farms', 'classified_count',
                'unclassified_count', 'group_counts', 'summary_df'

        Returns:
            DataFrame with comparison metrics across all modes

        Note:
            The comparison includes:
            - Total farms analyzed
            - Classification success rates
            - Group distribution counts and percentages
            - Key statistics per group (if available)
        """
        comparison_data = []

        # Mode ordering (for consistent display)
        mode_order = [
            "6-indicators",
            "6-indicators-flex",
            "4-indicators",
            "5-indicators",
            "5-indicators-flex",
        ]

        # Sort modes according to defined order
        sorted_modes = sorted(
            mode_results.keys(), key=lambda x: mode_order.index(x) if x in mode_order else 999
        )

        # Section 1: Overall classification metrics
        comparison_data.append(
            {"Metric": "=== OVERALL CLASSIFICATION ===", **{mode: "" for mode in sorted_modes}}
        )

        # Total farms (should be same for all modes)
        total_farms_row = {"Metric": "Total Farms"}
        for mode in sorted_modes:
            total_farms_row[mode] = mode_results[mode].get("total_farms", 0)
        comparison_data.append(total_farms_row)

        # Classified farms count
        classified_row = {"Metric": "Classified Farms"}
        for mode in sorted_modes:
            classified_row[mode] = mode_results[mode].get("classified_count", 0)
        comparison_data.append(classified_row)

        # Unclassified farms count
        unclassified_row = {"Metric": "Unclassified Farms"}
        for mode in sorted_modes:
            unclassified_row[mode] = mode_results[mode].get("unclassified_count", 0)
        comparison_data.append(unclassified_row)

        # Classification success rate
        success_rate_row = {"Metric": "Success Rate (%)"}
        for mode in sorted_modes:
            total = mode_results[mode].get("total_farms", 0)
            classified = mode_results[mode].get("classified_count", 0)
            rate = (classified / total * 100) if total > 0 else 0
            success_rate_row[mode] = f"{rate:.1f}%"
        comparison_data.append(success_rate_row)

        # Empty row for spacing
        comparison_data.append({"Metric": "", **{mode: "" for mode in sorted_modes}})

        # Section 2: Group distribution
        comparison_data.append(
            {"Metric": "=== GROUP DISTRIBUTION ===", **{mode: "" for mode in sorted_modes}}
        )

        # Get all unique groups across all modes
        all_groups = set()
        for mode in sorted_modes:
            group_counts = mode_results[mode].get("group_counts", {})
            all_groups.update(group_counts.keys())

        # Define group ordering
        group_order = ["Muku", "Muku_Amme", "Milchvieh", "BKMmZ", "BKMoZ", "IKM", "Unclassified"]
        sorted_groups = sorted(
            all_groups, key=lambda x: group_order.index(x) if x in group_order else 999
        )

        # Add row for each group
        for group_name in sorted_groups:
            if group_name != "Unclassified":  # Handle unclassified separately
                group_row = {"Metric": f"{group_name} Count"}
                for mode in sorted_modes:
                    group_counts = mode_results[mode].get("group_counts", {})
                    count = group_counts.get(group_name, 0)
                    group_row[mode] = count
                comparison_data.append(group_row)

                # Add percentage row
                pct_row = {"Metric": f"{group_name} (%)"}
                for mode in sorted_modes:
                    group_counts = mode_results[mode].get("group_counts", {})
                    classified = mode_results[mode].get("classified_count", 0)
                    count = group_counts.get(group_name, 0)
                    pct = (count / classified * 100) if classified > 0 else 0
                    pct_row[mode] = f"{pct:.1f}%"
                comparison_data.append(pct_row)

        # Create DataFrame
        comparison_df = pd.DataFrame(comparison_data)

        logger.info(f"Created comparison summary for {len(sorted_modes)} modes")
        return comparison_df

    def print_summary(self) -> None:
        """
        Print a formatted summary of the analysis to console.

        This provides a quick overview of the classification results
        and key statistics.
        """
        print("\n" + "=" * 70)
        print("MuKa Farm Classification Summary")
        print("=" * 70)

        # Overall counts
        total_farms = len(self.farms)
        classified_farms = sum(1 for farm in self.farms if farm.group is not None)
        unclassified_farms = total_farms - classified_farms

        print(f"\nTotal farms analyzed: {total_farms}")
        print(
            f"Successfully classified: {classified_farms} ({classified_farms/total_farms*100:.1f}%)"
        )
        print(f"Unclassified: {unclassified_farms} ({unclassified_farms/total_farms*100:.1f}%)")

        # Group counts
        print("\n" + "-" * 70)
        print("Farms per Group:")
        print("-" * 70)

        counts = self.get_group_counts()
        for group_name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            if group_name != "Unclassified":
                percentage = (count / classified_farms * 100) if classified_farms > 0 else 0
                print(f"  {group_name:20s}: {count:5d} ({percentage:5.1f}%)")

        # Summary statistics
        print("\n" + "-" * 70)
        print("Summary Statistics by Group:")
        print("-" * 70)

        summary = self.get_summary_by_group()
        print(summary.to_string(index=False))

        print("\n" + "=" * 70 + "\n")
