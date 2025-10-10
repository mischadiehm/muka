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
