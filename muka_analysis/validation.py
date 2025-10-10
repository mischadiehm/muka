"""
Validation system for comparing classification results with reference data.

This module provides an extensible validation framework where ad-hoc validation
functions can be easily added to verify classification results against ground truth
or reference data.
"""

import logging
from typing import Any, Callable, Dict, List

import pandas as pd
from pydantic import BaseModel, Field

from muka_analysis.models import FarmData

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """
    Result of a validation check.

    Attributes:
        validation_name: Name of the validation function
        passed: Whether the validation passed
        message: Human-readable message about the result
        details: Additional details about the validation
        metrics: Quantitative metrics from the validation
    """

    validation_name: str = Field(..., description="Name of the validation function")
    passed: bool = Field(..., description="Whether validation passed")
    message: str = Field(..., description="Human-readable validation message")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional validation details"
    )
    metrics: Dict[str, float] = Field(default_factory=dict, description="Quantitative metrics")


class GroupComparison(BaseModel):
    """
    Comparison between predicted and reference groups.

    Attributes:
        group_name: Name of the group
        predicted_count: Count from our classification
        reference_count: Count from reference data
        difference: Absolute difference
        difference_pct: Percentage difference
    """

    group_name: str = Field(..., description="Group name")
    predicted_count: int = Field(..., ge=0, description="Predicted count")
    reference_count: int = Field(..., ge=0, description="Reference count")
    difference: int = Field(..., description="Absolute difference")
    difference_pct: float = Field(..., description="Percentage difference")


class ValidationSuite:
    """
    Suite of validation functions for classification results.

    This class provides an extensible framework to add and run validation
    functions that compare classification results with reference data.
    """

    def __init__(self) -> None:
        """Initialize the validation suite with default validators."""
        self.validators: Dict[str, Callable] = {}
        self._register_default_validators()

    def _register_default_validators(self) -> None:
        """Register default validation functions."""
        self.register_validator("group_comparison", self.validate_group_comparison)

    def register_validator(
        self, name: str, validator_func: Callable[..., ValidationResult]
    ) -> None:
        """
        Register a new validation function.

        Args:
            name: Unique name for the validator
            validator_func: Function that performs validation and returns ValidationResult

        Raises:
            ValueError: If validator name already exists
        """
        if name in self.validators:
            raise ValueError(f"Validator '{name}' is already registered")

        self.validators[name] = validator_func
        logger.info(f"Registered validator: {name}")

    def run_all_validations(
        self,
        classified_farms: List[FarmData],
        reference_df: pd.DataFrame,
    ) -> List[ValidationResult]:
        """
        Run all registered validation functions.

        Args:
            classified_farms: List of farms with our classifications
            reference_df: DataFrame containing reference data including 'group' column

        Returns:
            List of ValidationResult objects

        Example:
            >>> suite = ValidationSuite()
            >>> results = suite.run_all_validations(farms, reference_df)
            >>> for result in results:
            ...     print(f"{result.validation_name}: {'PASS' if result.passed else 'FAIL'}")
        """
        results: List[ValidationResult] = []

        for name, validator_func in self.validators.items():
            logger.info(f"Running validation: {name}")
            try:
                result = validator_func(classified_farms, reference_df)
                results.append(result)
                logger.info(f"  Result: {'PASS' if result.passed else 'FAIL'}")
            except Exception as e:
                logger.error(f"  Error in validation '{name}': {e}")
                results.append(
                    ValidationResult(
                        validation_name=name,
                        passed=False,
                        message=f"Validation failed with error: {str(e)}",
                        details={"error": str(e)},
                    )
                )

        return results

    def validate_group_comparison(
        self,
        classified_farms: List[FarmData],
        reference_df: pd.DataFrame,
        tolerance_pct: float = 5.0,
    ) -> ValidationResult:
        """
        Compare our classification results with the reference 'group' column.

        This validation:
        1. Counts farms in each group from our classification
        2. Counts farms in each group from the reference 'group' column
        3. Compares the counts and calculates differences
        4. Validates that differences are within acceptable tolerance

        Args:
            classified_farms: List of farms with our classifications
            reference_df: DataFrame with 'group' column
            tolerance_pct: Acceptable percentage difference (default 5%)

        Returns:
            ValidationResult with comparison details

        Raises:
            ValueError: If 'group' column is missing from reference_df
        """
        if "group" not in reference_df.columns:
            raise ValueError("Reference DataFrame must contain 'group' column")

        # Get our predicted group counts
        predicted_counts: Dict[str, int] = {}
        for farm in classified_farms:
            if farm.group is not None:
                group_name = farm.group.value if hasattr(farm.group, "value") else str(farm.group)
                predicted_counts[group_name] = predicted_counts.get(group_name, 0) + 1

        # Get reference group counts
        reference_counts = reference_df["group"].value_counts().to_dict()

        # Handle NaN/None in reference counts
        reference_counts_clean = {
            str(k): int(v) for k, v in reference_counts.items() if pd.notna(k)
        }

        # Get all unique group names
        all_groups = set(predicted_counts.keys()) | set(reference_counts_clean.keys())

        # Create comparisons
        comparisons: List[GroupComparison] = []
        max_diff_pct = 0.0

        for group_name in sorted(all_groups):
            pred_count = predicted_counts.get(group_name, 0)
            ref_count = reference_counts_clean.get(group_name, 0)
            diff = pred_count - ref_count

            # Calculate percentage difference (based on reference count)
            if ref_count > 0:
                diff_pct = (abs(diff) / ref_count) * 100
            elif pred_count > 0:
                diff_pct = 100.0  # 100% difference if we predicted but reference is 0
            else:
                diff_pct = 0.0

            max_diff_pct = max(max_diff_pct, diff_pct)

            comparisons.append(
                GroupComparison(
                    group_name=group_name,
                    predicted_count=pred_count,
                    reference_count=ref_count,
                    difference=diff,
                    difference_pct=diff_pct,
                )
            )

        # Check if validation passed
        passed = max_diff_pct <= tolerance_pct

        # Create detailed message
        total_predicted = sum(predicted_counts.values())
        total_reference = sum(reference_counts_clean.values())

        message_lines = [
            f"Group Comparison Validation: {'PASSED' if passed else 'FAILED'}",
            f"Total farms - Predicted: {total_predicted}, Reference: {total_reference}",
            f"Maximum difference: {max_diff_pct:.2f}% (tolerance: {tolerance_pct}%)",
            "\nGroup-by-group comparison:",
        ]

        for comp in comparisons:
            status = "✓" if comp.difference_pct <= tolerance_pct else "✗"
            message_lines.append(
                f"  {status} {comp.group_name}: "
                f"Predicted={comp.predicted_count}, "
                f"Reference={comp.reference_count}, "
                f"Diff={comp.difference:+d} ({comp.difference_pct:.2f}%)"
            )

        message = "\n".join(message_lines)

        # Create details dictionary
        details = {
            "comparisons": [comp.model_dump() for comp in comparisons],
            "total_predicted": total_predicted,
            "total_reference": total_reference,
            "tolerance_pct": tolerance_pct,
        }

        # Create metrics
        metrics = {
            "max_difference_pct": max_diff_pct,
            "total_predicted": float(total_predicted),
            "total_reference": float(total_reference),
            "num_groups": float(len(comparisons)),
        }

        return ValidationResult(
            validation_name="group_comparison",
            passed=passed,
            message=message,
            details=details,
            metrics=metrics,
        )

    def analyze_reference_groups(self, reference_df: pd.DataFrame) -> Dict[str, int]:
        """
        Analyze the reference 'group' column to understand its distribution.

        Args:
            reference_df: DataFrame with 'group' column

        Returns:
            Dictionary mapping group names to counts

        Raises:
            ValueError: If 'group' column is missing
        """
        if "group" not in reference_df.columns:
            raise ValueError("Reference DataFrame must contain 'group' column")

        # Get value counts including NaN
        value_counts = reference_df["group"].value_counts(dropna=False)

        # Log analysis
        logger.info("Reference group analysis:")
        logger.info(f"  Total records: {len(reference_df)}")
        logger.info(f"  Unique groups: {reference_df['group'].nunique()}")

        if reference_df["group"].isna().any():
            na_count = reference_df["group"].isna().sum()
            logger.info(f"  Missing/NA values: {na_count}")

        logger.info("  Group distribution:")
        for group, count in value_counts.items():
            logger.info(f"    {group}: {count}")

        # Return clean dictionary (exclude NaN)
        return {str(k): int(v) for k, v in value_counts.items() if pd.notna(k)}


def create_validation_report(
    validation_results: List[ValidationResult],
) -> pd.DataFrame:
    """
    Create a summary DataFrame from validation results.

    Args:
        validation_results: List of ValidationResult objects

    Returns:
        DataFrame with validation summary

    Example:
        >>> results = suite.run_all_validations(farms, reference_df)
        >>> report_df = create_validation_report(results)
        >>> print(report_df)
    """
    data = []
    for result in validation_results:
        row = {
            "Validation": result.validation_name,
            "Status": "PASS" if result.passed else "FAIL",
            "Message": result.message.split("\n")[0],  # First line only
        }
        # Add metrics as columns
        row.update(result.metrics)
        data.append(row)

    return pd.DataFrame(data)
