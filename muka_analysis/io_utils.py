"""
File I/O utilities for MuKa farm analysis.

This module handles reading and writing CSV files with proper validation
and error handling.
"""

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from muka_analysis.models import FarmData
from muka_analysis.validators import DataValidator

logger = logging.getLogger(__name__)


class IOUtils:
    """
    Utility class for file input/output operations.

    This class provides methods to read farm data from CSV files and
    write results back to CSV files with proper validation and error handling.
    """

    @staticmethod
    def read_csv(file_path: Path, validate: bool = True) -> pd.DataFrame:
        """
        Read a CSV file into a pandas DataFrame.

        Args:
            file_path: Path to the CSV file
            validate: Whether to run validation checks on the data

        Returns:
            pandas DataFrame with the CSV data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is empty or has invalid structure
            pd.errors.ParserError: If CSV parsing fails

        Example:
            >>> from pathlib import Path
            >>> df = IOUtils.read_csv(Path("data/farms.csv"))
            >>> print(df.shape)
        """
        # Validate file exists
        DataValidator.validate_file_exists(file_path)

        try:
            # Read CSV with appropriate settings
            # Skip the first row (description row) and use second row as header
            df = pd.read_csv(
                file_path,
                encoding="utf-8",
                skiprows=[0],  # Skip first row with descriptions
                on_bad_lines="warn",
            )

            # Remove unnamed columns (often artifacts from Excel exports)
            unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]
            if unnamed_cols:
                df = df.drop(columns=unnamed_cols)

            logger.info(f"Successfully read {len(df)} rows from {file_path}")

            if validate:
                df, warnings = DataValidator.validate_all(df)
                if warnings:
                    logger.warning(f"Validation warnings: {len(warnings)}")
                    for warning in warnings[:10]:  # Log first 10 warnings
                        logger.warning(f"  - {warning}")

            return df

        except pd.errors.ParserError as e:
            logger.error(f"Failed to parse CSV file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            raise

    @staticmethod
    def dataframe_to_farm_data(df: pd.DataFrame) -> List[FarmData]:
        """
        Convert a pandas DataFrame to a list of FarmData objects.

        Args:
            df: DataFrame containing farm data

        Returns:
            List of validated FarmData objects

        Raises:
            ValueError: If data validation fails for any row

        Note:
            This method uses Pydantic validation, so any data quality
            issues will raise detailed validation errors.
        """
        farms: List[FarmData] = []
        errors: List[str] = []

        for idx, row in df.iterrows():
            try:
                farm = FarmData(
                    tvd=int(row["tvd"]),
                    farm_type_name=str(row["farmTypeName"]),
                    year=int(row["Jahr"]),
                    n_animals_total=int(row["n_animals_total"]),
                    n_females_age3_dairy=int(row["n_females_age3_dairy"]),
                    n_days_female_age3_dairy=float(row["n_days_female_age3_dairy"]),
                    prop_days_female_age3_dairy=float(row["prop_days_female_age3_dairy"]),
                    n_females_age3_total=int(row["n_females_age3_total"]),
                    n_total_entries_younger85=int(row["n_total_entries_younger85"]),
                    n_total_leavings_younger51=int(row["n_total_leavings_younger51"]),
                    n_females_younger731=int(row["n_females_younger731"]),
                    prop_females_slaughterings_younger731=float(
                        row["prop_females_slaughterings_younger731"]
                    ),
                    n_animals_from51_to730=int(row["n_animals_from51_to730"]),
                    indicator_female_dairy_cattle_v2=int(row["1_femaleDairyCattle_V2"]),
                    indicator_female_cattle=int(row["2_femaleCattle"]),
                    indicator_calf_arrivals=int(row["3_calf85Arrivals"]),
                    indicator_calf_leavings=int(row["5_calf51nonSlaughterLeavings"]),
                    indicator_female_slaughterings=int(row["6_female731Slaughterings"]),
                    indicator_young_slaughterings=int(row["7_young51to730Slaughterings"]),
                )
                farms.append(farm)

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        if errors:
            logger.error(f"Failed to parse {len(errors)} rows out of {len(df)}")
            if len(errors) == len(df):
                raise ValueError(f"Failed to parse all rows. First error: {errors[0]}")

        logger.info(f"Successfully converted {len(farms)} rows to FarmData objects")
        return farms

    @staticmethod
    def farm_data_to_dataframe(farms: List[FarmData]) -> pd.DataFrame:
        """
        Convert a list of FarmData objects to a pandas DataFrame.

        Args:
            farms: List of FarmData objects

        Returns:
            pandas DataFrame with farm data

        Note:
            The DataFrame will include all fields from FarmData, including
            the assigned 'group' field.
        """
        data = []
        for farm in farms:
            data.append(
                {
                    "tvd": farm.tvd,
                    "farmTypeName": farm.farm_type_name,
                    "Jahr": farm.year,
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
                    "1_femaleDairyCattle_V2": farm.indicator_female_dairy_cattle_v2,
                    "2_femaleCattle": farm.indicator_female_cattle,
                    "3_calf85Arrivals": farm.indicator_calf_arrivals,
                    "5_calf51nonSlaughterLeavings": farm.indicator_calf_leavings,
                    "6_female731Slaughterings": farm.indicator_female_slaughterings,
                    "7_young51to730Slaughterings": farm.indicator_young_slaughterings,
                    "group": (
                        farm.group.value
                        if farm.group and hasattr(farm.group, "value")
                        else farm.group
                    ),
                }
            )

        df = pd.DataFrame(data)
        logger.info(f"Converted {len(farms)} FarmData objects to DataFrame")
        return df

    @staticmethod
    def write_csv(df: pd.DataFrame, file_path: Path, include_bom: bool = True) -> None:
        """
        Write a DataFrame to a CSV file.

        Args:
            df: DataFrame to write
            file_path: Output file path
            include_bom: Whether to include UTF-8 BOM (for Excel compatibility)

        Raises:
            PermissionError: If the file cannot be written
            OSError: If there's a file system error

        Note:
            The output directory will be created if it doesn't exist.
        """
        # Create output directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Write with UTF-8 encoding and optional BOM
            encoding = "utf-8-sig" if include_bom else "utf-8"
            df.to_csv(file_path, index=False, encoding=encoding)

            logger.info(f"Successfully wrote {len(df)} rows to {file_path}")

        except PermissionError as e:
            logger.error(f"Permission denied writing to {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to write CSV to {file_path}: {e}")
            raise

    @staticmethod
    def read_and_parse(file_path: Path) -> List[FarmData]:
        """
        Convenience method to read CSV and parse to FarmData objects in one step.

        Args:
            file_path: Path to CSV file

        Returns:
            List of validated FarmData objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data validation fails
        """
        df = IOUtils.read_csv(file_path, validate=True)
        farms = IOUtils.dataframe_to_farm_data(df)
        return farms

    @staticmethod
    def write_results(farms: List[FarmData], file_path: Path, include_bom: bool = True) -> None:
        """
        Convenience method to convert FarmData to DataFrame and write to CSV.

        Args:
            farms: List of FarmData objects to write
            file_path: Output file path
            include_bom: Whether to include UTF-8 BOM
        """
        df = IOUtils.farm_data_to_dataframe(farms)
        IOUtils.write_csv(df, file_path, include_bom=include_bom)
