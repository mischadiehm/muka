"""
Pydantic models for MuKa farm data validation and processing.

This module defines the data structures used throughout the analysis pipeline,
ensuring type safety and data validation at every step.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class IndicatorMode(str, Enum):
    """
    Enumeration of indicator modes for farm classification.

    Defines which indicators are used in the classification algorithm.

    Attributes:
        SIX_INDICATORS: Use all 6 indicators (NEW method, most strict)
            - All fields have specific values for ALL groups including Milchvieh
            - Milchvieh: [1, 0, 0, 1, 0, 0] (strict on all 6 fields)
        SIX_INDICATORS_FLEX: Use all 6 indicators with Milchvieh field 6 flexibility
            - Field 5 matters for all groups (strict)
            - Field 6: Milchvieh accepts any value (0||1), others have specific values
            - Milchvieh: [1, 0, 0, 1, 0, *] (flexible only on field 6)
        FOUR_INDICATORS: Use only first 4 indicators (OLD method, most flexible)
            - Ignores both slaughter fields (fields 5 & 6 = *)
        FIVE_INDICATORS: Use 5 indicators, ignore female_slaughterings
            - Field 5 (female_slaughterings) = * for all groups
            - Field 6 (young_slaughterings) has specific values
        FIVE_INDICATORS_FLEX: Use 5 indicators with Milchvieh flexibility
            - Field 5 (female_slaughterings) = * for all groups
            - Field 6 (young_slaughterings) = * only for Milchvieh, specific for others
    """

    SIX_INDICATORS = "6-indicators"
    SIX_INDICATORS_FLEX = "6-indicators-flex"
    FOUR_INDICATORS = "4-indicators"
    FIVE_INDICATORS = "5-indicators"
    FIVE_INDICATORS_FLEX = "5-indicators-flex"


class FarmGroup(str, Enum):
    """
    Enumeration of farm group classifications.

    Each farm is classified into one of these groups based on specific
    criteria related to cattle types and movements.

    Attributes:
        MUKU: Mother cow farms without nurse cows (no dairy cattle, no arrivals)
        MUKU_AMME: Mother cow farms with nurse cows (no dairy, has calf arrivals)
        MILCHVIEH: Dairy farms (has dairy cattle and non-slaughter leavings)
        BKMMZ: Combined keeping dairy with breeding (dairy + calf arrivals)
        BKMOZ: Combined keeping dairy without breeding (dairy, no arrivals)
        IKM: Intensive calf rearing (no dairy, has female cattle + arrivals)
    """

    MUKU = "Muku"
    MUKU_AMME = "Muku_Amme"
    MILCHVIEH = "Milchvieh"
    BKMMZ = "BKMmZ"
    BKMOZ = "BKMoZ"
    IKM = "IKM"


class GroupProfile(BaseModel):
    """
    Profile definition for farm group classification.

    This model defines the binary pattern used to classify farms into groups.
    Each attribute represents a specific criterion that must match for the farm
    to be classified into that group.

    Attributes:
        group_name: Name of the farm group
        female_dairy_cattle: Whether farm has female dairy cattle (1) or not (0)
        female_cattle: Whether farm has female cattle other than dairy (1) or not (0)
        calf_arrivals: Whether farm has calf arrivals under 85 days (1) or not (0)
        calf_non_slaughter_leavings: Whether farm has non-slaughter leavings under 51 days (1) or not (0)
        female_slaughterings: Whether farm has female slaughterings <731 days (1) or not (0), or None for any
        young_slaughterings: Whether farm has young slaughterings 51-730 days (1) or not (0), or None for any
    """

    group_name: FarmGroup
    female_dairy_cattle: int = Field(
        ..., ge=0, le=1, description="Binary indicator for female dairy cattle"
    )
    female_cattle: int = Field(
        ..., ge=0, le=1, description="Binary indicator for other female cattle"
    )
    calf_arrivals: int = Field(
        ..., ge=0, le=1, description="Binary indicator for calf arrivals <85 days"
    )
    calf_non_slaughter_leavings: int = Field(
        ..., ge=0, le=1, description="Binary indicator for calf leavings <51 days"
    )
    female_slaughterings: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description="Binary indicator for female slaughterings <731 days (None = any)",
    )
    young_slaughterings: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description="Binary indicator for young slaughterings 51-730 days (None = any)",
    )

    @field_validator(
        "female_dairy_cattle",
        "female_cattle",
        "calf_arrivals",
        "calf_non_slaughter_leavings",
        "female_slaughterings",
        "young_slaughterings",
    )
    @classmethod
    def validate_binary(cls, v: Optional[int]) -> Optional[int]:
        """Validate that value is binary (0 or 1) or None."""
        if v is not None and v not in [0, 1]:
            raise ValueError(f"Value must be 0, 1, or None, got {v}")
        return v

    def matches(
        self,
        female_dairy: int,
        female_cattle: int,
        calf_arrivals: int,
        calf_leavings: int,
        female_slaughter: int,
        young_slaughter: int,
    ) -> bool:
        """
        Check if a farm's criteria match this profile.

        Args:
            female_dairy: Binary indicator for female dairy cattle
            female_cattle: Binary indicator for other female cattle
            calf_arrivals: Binary indicator for calf arrivals
            calf_leavings: Binary indicator for calf non-slaughter leavings
            female_slaughter: Binary indicator for female slaughterings <731 days
            young_slaughter: Binary indicator for young slaughterings 51-730 days

        Returns:
            True if all criteria match this profile, False otherwise

        Note:
            If a profile field is None, it matches any value for that field.
        """
        return (
            self.female_dairy_cattle == female_dairy
            and self.female_cattle == female_cattle
            and self.calf_arrivals == calf_arrivals
            and self.calf_non_slaughter_leavings == calf_leavings
            and (self.female_slaughterings is None or self.female_slaughterings == female_slaughter)
            and (self.young_slaughterings is None or self.young_slaughterings == young_slaughter)
        )


class FarmData(BaseModel):
    """
    Validated farm data record.

    This model represents a single farm's data with all relevant metrics
    for classification and analysis. All numeric fields are validated to ensure
    they meet expected constraints.

    Attributes:
        tvd: Farm identification number
        farm_type_name: Type of farm operation
        year: Year of data collection
        n_animals_total: Total number of animals on farm
        n_females_age3_dairy: Number of female dairy cattle aged 3+
        n_days_female_age3_dairy: Total days for female dairy cattle aged 3+
        prop_days_female_age3_dairy: Proportion of days for female dairy cattle
        n_females_age3_total: Total number of female cattle aged 3+
        n_total_entries_younger85: Total entries of animals younger than 85 days
        n_total_leavings_younger51: Total leavings of animals younger than 51 days
        n_females_younger731: Number of females younger than 731 days
        prop_females_slaughterings_younger731: Proportion of female slaughterings <731 days
        n_animals_from51_to730: Number of animals aged 51-730 days
        indicator_female_dairy_cattle_v2: Binary indicator for female dairy cattle (version 2)
        indicator_female_cattle: Binary indicator for other female cattle
        indicator_calf_arrivals: Binary indicator for calf arrivals
        indicator_calf_leavings: Binary indicator for calf non-slaughter leavings
        group: Assigned farm group (optional, set during classification)
    """

    tvd: int = Field(..., description="Farm TVD identification number")
    farm_type_name: str = Field(..., description="Farm type name")
    year: int = Field(..., ge=2000, le=2100, description="Year of data collection")

    # Animal counts
    n_animals_total: int = Field(..., ge=0, description="Total number of animals")
    n_females_age3_dairy: int = Field(
        ..., ge=0, description="Number of female dairy cattle 3+ years"
    )
    n_days_female_age3_dairy: float = Field(
        ..., ge=0, description="Total days for female dairy 3+ years"
    )
    prop_days_female_age3_dairy: float = Field(
        ..., ge=0, le=1, description="Proportion of days female dairy"
    )
    n_females_age3_total: int = Field(..., ge=0, description="Total female cattle 3+ years")

    # Movements
    n_total_entries_younger85: int = Field(..., ge=0, description="Total entries <85 days")
    n_total_leavings_younger51: int = Field(..., ge=0, description="Total leavings <51 days")

    # Slaughter data
    n_females_younger731: int = Field(..., ge=0, description="Females <731 days")
    prop_females_slaughterings_younger731: float = Field(
        ..., ge=0, le=1, description="Proportion female slaughterings <731 days"
    )
    n_animals_from51_to730: int = Field(..., ge=0, description="Animals aged 51-730 days")

    # Binary indicators for classification
    indicator_female_dairy_cattle_v2: int = Field(
        ..., ge=0, le=1, description="Binary: has female dairy cattle"
    )
    indicator_female_cattle: int = Field(
        ..., ge=0, le=1, description="Binary: has other female cattle"
    )
    indicator_calf_arrivals: int = Field(
        ..., ge=0, le=1, description="Binary: has calf arrivals <85 days"
    )
    indicator_calf_leavings: int = Field(
        ..., ge=0, le=1, description="Binary: has calf leavings <51 days"
    )
    indicator_female_slaughterings: int = Field(
        ..., ge=0, le=1, description="Binary: has female slaughterings <731 days"
    )
    indicator_young_slaughterings: int = Field(
        ..., ge=0, le=1, description="Binary: has young slaughterings 51-730 days"
    )

    # Classification result
    group: Optional[FarmGroup] = Field(None, description="Assigned farm group")

    @field_validator("prop_days_female_age3_dairy", "prop_females_slaughterings_younger731")
    @classmethod
    def validate_proportion(cls, v: float) -> float:
        """Validate that proportions are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError(f"Proportion must be between 0 and 1, got {v}")
        return v

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True
        validate_assignment = True


class GroupSummaryStats(BaseModel):
    """
    Summary statistics for a farm group.

    This model contains aggregated statistics (min, max, mean, median)
    for all numeric metrics within a specific farm group.

    Attributes:
        group: Farm group name
        count: Number of farms in this group
        stats: Dictionary of statistics for each metric
    """

    group: FarmGroup
    count: int = Field(..., ge=0, description="Number of farms in group")
    stats: Dict[str, Dict[str, float]] = Field(
        ..., description="Statistics dictionary: {metric_name: {stat_type: value}}"
    )

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True


class ClassificationResult(BaseModel):
    """
    Result of farm classification process.

    Contains the classified farms data and summary information about
    the classification results.

    Attributes:
        farms: List of classified farm data
        total_farms: Total number of farms processed
        classified_farms: Number of successfully classified farms
        unclassified_farms: Number of farms that couldn't be classified
        group_counts: Dictionary of farm counts per group
    """

    farms: List[FarmData]
    total_farms: int = Field(..., ge=0)
    classified_farms: int = Field(..., ge=0)
    unclassified_farms: int = Field(..., ge=0)
    group_counts: Dict[str, int] = Field(default_factory=dict)

    @field_validator("farms")
    @classmethod
    def validate_farms_list(cls, v: List[FarmData]) -> List[FarmData]:
        """Ensure farms list is not empty."""
        if not v:
            raise ValueError("Farms list cannot be empty")
        return v

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True


class ModeAnalysisResult(BaseModel):
    """
    Results from analyzing farms with a specific indicator mode.

    This model stores complete analysis results for one indicator mode,
    including classification results and summary statistics.

    Attributes:
        mode: Indicator mode used (e.g., '4-indicators')
        farms: List of classified farm data
        total_farms: Total number of farms processed
        classified_count: Number of successfully classified farms
        unclassified_count: Number of farms that couldn't be classified
        group_counts: Dictionary mapping group names to farm counts
        group_percentages: Dictionary mapping group names to percentages
        summary_stats: Summary statistics by group
    """

    mode: str = Field(..., description="Indicator mode name")
    farms: List[FarmData] = Field(..., description="Classified farm data")
    total_farms: int = Field(..., ge=0, description="Total farms analyzed")
    classified_count: int = Field(..., ge=0, description="Successfully classified farms")
    unclassified_count: int = Field(..., ge=0, description="Unclassified farms")
    group_counts: Dict[str, int] = Field(default_factory=dict, description="Farm counts per group")
    group_percentages: Dict[str, float] = Field(
        default_factory=dict, description="Percentage of classified farms per group"
    )
    summary_stats: Optional[Any] = Field(
        default=None, description="Summary statistics DataFrame (stored as dict)"
    )

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate that mode is one of the known indicator modes."""
        valid_modes = {
            "6-indicators",
            "6-indicators-flex",
            "4-indicators",
            "5-indicators",
            "5-indicators-flex",
        }
        if v not in valid_modes:
            raise ValueError(f"Invalid mode '{v}'. Must be one of: {valid_modes}")
        return v

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True


class ModeComparisonSummary(BaseModel):
    """
    Summary comparison of results across multiple indicator modes.

    This model stores comparative analysis showing how different
    indicator modes affect farm classification.

    Attributes:
        modes: List of indicator modes compared
        total_farms: Total number of farms analyzed (same across all modes)
        mode_results: Dictionary mapping mode names to their results
        classification_comparison: Comparison of classification success rates
        group_distribution_comparison: Comparison of group distributions
        farms_with_different_classifications: List of farm IDs that classify differently
    """

    modes: List[str] = Field(..., description="List of modes compared")
    total_farms: int = Field(..., ge=0, description="Total farms analyzed")
    mode_results: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Results summary per mode"
    )
    classification_success_rates: Dict[str, float] = Field(
        default_factory=dict, description="Classification success rate per mode (percentage)"
    )
    group_distribution_comparison: Dict[str, Dict[str, int]] = Field(
        default_factory=dict, description="Group counts per mode"
    )
    farms_with_different_classifications: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Farms that classify differently across modes"
    )

    @field_validator("modes")
    @classmethod
    def validate_modes_list(cls, v: List[str]) -> List[str]:
        """Ensure at least 2 modes are being compared."""
        if len(v) < 2:
            raise ValueError("Must compare at least 2 modes")
        return v

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
