"""
Statistical analysis for MuKa farm data.

This module provides functions to analyze classified farm data and
generate summary statistics by group.
"""

import logging
from typing import Dict, List, Optional

import pandas as pd

from muka_analysis.models import FarmData, FarmGroup, GroupSummaryStats

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
        "prop_days_female_age3_dairy",
        "n_females_age3_total",
        "n_total_entries_younger85",
        "n_total_leavings_younger51",
        "n_females_younger731",
        "prop_females_slaughterings_younger731",
        "n_animals_from51_to730",
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
            DataFrame with all farm data
        """
        data = []
        for farm in self.farms:
            data.append(
                {
                    "tvd": farm.tvd,
                    "year": farm.year,
                    "group": (
                        farm.group.value
                        if farm.group and hasattr(farm.group, "value")
                        else farm.group
                    ),
                    "n_animals_total": farm.n_animals_total,
                    "n_females_age3_dairy": farm.n_females_age3_dairy,
                    "n_days_female_age3_dairy": farm.n_days_female_age3_dairy,
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

        logger.info(f"Group counts: {counts}")
        return counts

    def calculate_group_statistics(self, group: Optional[FarmGroup] = None) -> pd.DataFrame:
        """
        Calculate descriptive statistics for numeric fields by group.

        Args:
            group: Specific group to analyze, or None for all groups

        Returns:
            DataFrame with statistics (min, max, mean, median) for each group

        Note:
            Statistics are calculated for all numeric fields defined in
            NUMERIC_FIELDS.
        """
        if group is not None:
            group_df = self.df[self.df["group"] == group.value]
            if group_df.empty:
                logger.warning(f"No farms found in group {group.value}")
                return pd.DataFrame()
            dfs_to_analyze = {group.value: group_df}
        else:
            # Group by farm group
            dfs_to_analyze = {
                name: group_df for name, group_df in self.df.groupby("group") if pd.notna(name)
            }

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
        logger.info(f"Calculated statistics for {len(all_stats)} groups")

        return stats_df

    def get_summary_by_group(self) -> pd.DataFrame:
        """
        Get a summary table with key metrics by group.

        Returns:
            DataFrame with summary statistics for each group

        Note:
            This provides a condensed view with the most important metrics.
        """
        summary_stats = self.calculate_group_statistics()

        # Select key columns for summary
        key_columns = [
            "group",
            "count",
            "n_animals_total_mean",
            "n_animals_total_median",
            "n_females_age3_total_mean",
            "n_females_age3_total_median",
            "n_total_entries_younger85_mean",
            "n_total_leavings_younger51_mean",
        ]

        available_columns = [col for col in key_columns if col in summary_stats.columns]
        summary = summary_stats[available_columns]

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

    def export_summary_to_excel(self, file_path: str) -> None:
        """
        Export analysis summary to an Excel file with multiple sheets.

        Args:
            file_path: Path to output Excel file

        Note:
            Creates an Excel file with the following sheets:
            - Summary: Overview statistics by group
            - Detailed_Stats: Full statistics for all metrics
            - Group_Counts: Farm counts per group
        """
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Summary sheet
            summary = self.get_summary_by_group()
            summary.to_excel(writer, sheet_name="Summary", index=False)

            # Detailed statistics sheet
            detailed_stats = self.calculate_group_statistics()
            detailed_stats.to_excel(writer, sheet_name="Detailed_Stats", index=False)

            # Group counts sheet
            counts = self.get_group_counts()
            counts_df = pd.DataFrame(list(counts.items()), columns=["Group", "Count"])
            counts_df.to_excel(writer, sheet_name="Group_Counts", index=False)

        logger.info(f"Exported analysis summary to {file_path}")

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
