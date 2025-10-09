"""
Data validation utilities for MuKa farm analysis.

This module provides validation functions to ensure data quality and
catch potential issues before processing.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validator for farm data quality checks.

    This class provides methods to validate CSV files, check for missing values,
    validate data types, and ensure data integrity before processing.
    """

    REQUIRED_COLUMNS: List[str] = [
        "tvd",
        "farmTypeName",
        "Jahr",
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
        "1_femaleDairyCattle_V2",
        "2_femaleCattle",
        "3_calf85Arrivals",
        "5_calf51nonSlaughterLeavings",
    ]

    NUMERIC_COLUMNS: List[str] = [
        "tvd",
        "Jahr",
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
        "1_femaleDairyCattle_V2",
        "2_femaleCattle",
        "3_calf85Arrivals",
        "5_calf51nonSlaughterLeavings",
    ]

    BINARY_COLUMNS: List[str] = [
        "1_femaleDairyCattle_V2",
        "2_femaleCattle",
        "3_calf85Arrivals",
        "5_calf51nonSlaughterLeavings",
    ]

    @staticmethod
    def validate_file_exists(file_path: Path) -> None:
        """
        Validate that a file exists and is readable.

        Args:
            file_path: Path to file to validate

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file is not readable
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if not file_path.stat().st_size > 0:
            raise ValueError(f"File is empty: {file_path}")

        logger.info(f"File validated: {file_path}")

    @staticmethod
    def validate_dataframe_structure(df: pd.DataFrame) -> None:
        """
        Validate that DataFrame has required columns and structure.

        Args:
            df: DataFrame to validate

        Raises:
            ValueError: If required columns are missing or structure is invalid
        """
        if df.empty:
            raise ValueError("DataFrame is empty")

        missing_columns = set(DataValidator.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        logger.info(f"DataFrame structure validated: {len(df)} rows, {len(df.columns)} columns")

    @staticmethod
    def validate_numeric_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validate and convert numeric columns to proper types.

        Args:
            df: DataFrame with columns to validate

        Returns:
            Tuple of (validated DataFrame, list of validation warnings)

        Raises:
            ValueError: If numeric conversion fails for critical columns
        """
        warnings: List[str] = []

        for col in DataValidator.NUMERIC_COLUMNS:
            if col not in df.columns:
                continue

            # Check for non-numeric values
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    null_count = df[col].isna().sum()
                    if null_count > 0:
                        warnings.append(
                            f"Column '{col}': Converted {null_count} non-numeric values to NaN"
                        )
                except Exception as e:
                    raise ValueError(f"Failed to convert column '{col}' to numeric: {e}")

        logger.info(f"Numeric columns validated with {len(warnings)} warnings")
        return df, warnings

    @staticmethod
    def validate_binary_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validate that binary indicator columns contain only 0 or 1.

        Args:
            df: DataFrame with binary columns to validate

        Returns:
            Tuple of (validated DataFrame, list of validation warnings)

        Raises:
            ValueError: If binary columns contain invalid values
        """
        warnings: List[str] = []

        for col in DataValidator.BINARY_COLUMNS:
            if col not in df.columns:
                continue

            # Check for values other than 0 or 1
            unique_values = df[col].dropna().unique()
            invalid_values = [v for v in unique_values if v not in [0, 1]]

            if invalid_values:
                raise ValueError(
                    f"Binary column '{col}' contains invalid values: {invalid_values}. "
                    f"Expected only 0 or 1."
                )

        logger.info("Binary columns validated successfully")
        return df, warnings

    @staticmethod
    def validate_proportions(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validate that proportion columns are between 0 and 1.

        Args:
            df: DataFrame with proportion columns to validate

        Returns:
            Tuple of (validated DataFrame, list of validation warnings)
        """
        warnings: List[str] = []
        proportion_cols = [
            "prop_days_female_age3_dairy",
            "prop_females_slaughterings_younger731",
        ]

        for col in proportion_cols:
            if col not in df.columns:
                continue

            # Check for values outside [0, 1]
            invalid_mask = (df[col] < 0) | (df[col] > 1)
            invalid_count = invalid_mask.sum()

            if invalid_count > 0:
                warnings.append(
                    f"Column '{col}': Found {invalid_count} values outside [0, 1] range"
                )
                # Log some examples
                invalid_examples = df.loc[invalid_mask, [col]].head()
                logger.warning(f"Invalid proportion examples:\n{invalid_examples}")

        logger.info(f"Proportion columns validated with {len(warnings)} warnings")
        return df, warnings

    @staticmethod
    def check_missing_values(df: pd.DataFrame) -> Dict[str, int]:
        """
        Check for missing values in all columns.

        Args:
            df: DataFrame to check

        Returns:
            Dictionary mapping column names to count of missing values
        """
        missing_counts = df.isnull().sum()
        missing_dict = missing_counts[missing_counts > 0].to_dict()

        if missing_dict:
            logger.warning(f"Found missing values in {len(missing_dict)} columns")
            for col, count in missing_dict.items():
                logger.warning(f"  {col}: {count} missing values")
        else:
            logger.info("No missing values found")

        return missing_dict

    @staticmethod
    def validate_data_ranges(df: pd.DataFrame) -> List[str]:
        """
        Validate that data values are within expected ranges.

        Args:
            df: DataFrame to validate

        Returns:
            List of validation warnings
        """
        warnings: List[str] = []

        # Check for negative counts (should not happen)
        count_columns = [
            "n_animals_total",
            "n_females_age3_dairy",
            "n_females_age3_total",
            "n_total_entries_younger85",
            "n_total_leavings_younger51",
            "n_females_younger731",
            "n_animals_from51_to730",
        ]

        for col in count_columns:
            if col not in df.columns:
                continue

            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                warnings.append(f"Column '{col}': Found {negative_count} negative values")

        # Check for unreasonable year values
        if "Jahr" in df.columns:
            year_min, year_max = df["Jahr"].min(), df["Jahr"].max()
            if year_min < 2000 or year_max > 2100:
                warnings.append(f"Year values outside expected range: [{year_min}, {year_max}]")

        if warnings:
            logger.warning(f"Data range validation produced {len(warnings)} warnings")
        else:
            logger.info("Data ranges validated successfully")

        return warnings

    @classmethod
    def validate_all(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Run all validation checks on a DataFrame.

        This is the main entry point for data validation. It runs all
        validation checks and returns the validated DataFrame along with
        any warnings encountered.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (validated DataFrame, list of all warnings)

        Raises:
            ValueError: If validation fails for critical issues
        """
        all_warnings: List[str] = []

        # Structure validation
        cls.validate_dataframe_structure(df)

        # Numeric conversion
        df, numeric_warnings = cls.validate_numeric_columns(df)
        all_warnings.extend(numeric_warnings)

        # Binary validation
        df, binary_warnings = cls.validate_binary_columns(df)
        all_warnings.extend(binary_warnings)

        # Proportion validation
        df, prop_warnings = cls.validate_proportions(df)
        all_warnings.extend(prop_warnings)

        # Missing values check
        missing_dict = cls.check_missing_values(df)
        if missing_dict:
            all_warnings.append(f"Missing values found in {len(missing_dict)} columns")

        # Range validation
        range_warnings = cls.validate_data_ranges(df)
        all_warnings.extend(range_warnings)

        logger.info(f"Validation complete: {len(all_warnings)} total warnings")

        return df, all_warnings
