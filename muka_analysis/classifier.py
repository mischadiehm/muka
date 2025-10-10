"""
Farm classification logic for MuKa analysis.

This module implements the classification algorithm that assigns farms to groups
based on their cattle type and movement patterns.
"""

import logging
from typing import List, Optional

from muka_analysis.config import get_config
from muka_analysis.models import FarmData, FarmGroup, GroupProfile

logger = logging.getLogger(__name__)


class FarmClassifier:
    """
    Classifier for assigning farms to groups based on binary indicators.

    This class implements the classification logic that maps farm characteristics
    (presence/absence of certain cattle types and movements) to predefined
    farm groups.

    The classification is based on a lookup table of profiles, where each profile
    defines the expected binary pattern for a specific farm group.
    """

    def __init__(self) -> None:
        """Initialize the classifier with predefined group profiles."""
        self.profiles: List[GroupProfile] = self._create_profiles()
        logger.info(f"Classifier initialized with {len(self.profiles)} group profiles")

    @staticmethod
    def _create_profiles() -> List[GroupProfile]:
        """
        Create the lookup table of farm group profiles.

        Each profile defines the expected binary pattern for classification.
        The pattern is based on four binary indicators:
        1. Female dairy cattle (1_femaleDairyCattle_V2)
        2. Other female cattle (2_femaleCattle)
        3. Calf arrivals under 85 days (3_calf85Arrivals)
        4. Calf non-slaughter leavings under 51 days (5_calf51nonSlaughterLeavings)

        Returns:
            List of GroupProfile objects defining each farm group

        Note:
            The order of profiles matters for classification priority.
            More specific patterns should come before more general ones.
        """
        profiles = [
            # Muku: Mother cow farms without nurse cows
            # No dairy cattle, no other female cattle, no arrivals, no leavings
            GroupProfile(
                group_name=FarmGroup.MUKU,
                female_dairy_cattle=0,
                female_cattle=0,
                calf_arrivals=0,
                calf_non_slaughter_leavings=0,
            ),
            # Muku_Amme: Mother cow farms with nurse cows
            # No dairy cattle, no other female cattle, has arrivals, no leavings
            GroupProfile(
                group_name=FarmGroup.MUKU_AMME,
                female_dairy_cattle=0,
                female_cattle=0,
                calf_arrivals=1,
                calf_non_slaughter_leavings=0,
            ),
            # Milchvieh: Dairy farms
            # Has dairy cattle, no other female cattle, no arrivals, has leavings
            GroupProfile(
                group_name=FarmGroup.MILCHVIEH,
                female_dairy_cattle=1,
                female_cattle=0,
                calf_arrivals=0,
                calf_non_slaughter_leavings=1,
            ),
            # BKMmZ: Combined keeping dairy with breeding
            # Has dairy cattle, no other female cattle, has arrivals, no leavings
            GroupProfile(
                group_name=FarmGroup.BKMMZ,
                female_dairy_cattle=1,
                female_cattle=0,
                calf_arrivals=1,
                calf_non_slaughter_leavings=0,
            ),
            # BKMoZ: Combined keeping dairy without breeding
            # Has dairy cattle, no other female cattle, no arrivals, no leavings
            GroupProfile(
                group_name=FarmGroup.BKMOZ,
                female_dairy_cattle=1,
                female_cattle=0,
                calf_arrivals=0,
                calf_non_slaughter_leavings=0,
            ),
            # IKM: Intensive calf rearing
            # No dairy cattle, has other female cattle, has arrivals, no leavings
            GroupProfile(
                group_name=FarmGroup.IKM,
                female_dairy_cattle=0,
                female_cattle=1,
                calf_arrivals=1,
                calf_non_slaughter_leavings=0,
            ),
        ]

        return profiles

    def classify_farm(self, farm: FarmData) -> Optional[FarmGroup]:
        """
        Classify a single farm based on its binary indicators.

        The classification matches the farm's binary indicator pattern against
        the predefined profiles. The first matching profile determines the group.

        Args:
            farm: FarmData object with binary indicators set

        Returns:
            FarmGroup if classification successful, None if no match found

        Example:
            >>> classifier = FarmClassifier()
            >>> farm = FarmData(
            ...     tvd=12345,
            ...     indicator_female_dairy_cattle_v2=1,
            ...     indicator_female_cattle=0,
            ...     indicator_calf_arrivals=0,
            ...     indicator_calf_leavings=1,
            ...     # ... other fields ...
            ... )
            >>> group = classifier.classify_farm(farm)
            >>> print(group)  # FarmGroup.MILCHVIEH
        """
        for profile in self.profiles:
            if profile.matches(
                female_dairy=farm.indicator_female_dairy_cattle_v2,
                female_cattle=farm.indicator_female_cattle,
                calf_arrivals=farm.indicator_calf_arrivals,
                calf_leavings=farm.indicator_calf_leavings,
            ):
                logger.debug(
                    f"Farm {farm.tvd} classified as {profile.group_name.value} "
                    f"[{farm.indicator_female_dairy_cattle_v2}, "
                    f"{farm.indicator_female_cattle}, "
                    f"{farm.indicator_calf_arrivals}, "
                    f"{farm.indicator_calf_leavings}]"
                )
                return profile.group_name

        # Only show warning if enabled in configuration
        config = get_config()
        if config.classification.show_unclassified_warnings:
            logger.warning(
                f"Farm {farm.tvd} could not be classified. Pattern: "
                f"[{farm.indicator_female_dairy_cattle_v2}, "
                f"{farm.indicator_female_cattle}, "
                f"{farm.indicator_calf_arrivals}, "
                f"{farm.indicator_calf_leavings}]"
            )
        else:
            logger.debug(
                f"Farm {farm.tvd} could not be classified. Pattern: "
                f"[{farm.indicator_female_dairy_cattle_v2}, "
                f"{farm.indicator_female_cattle}, "
                f"{farm.indicator_calf_arrivals}, "
                f"{farm.indicator_calf_leavings}]"
            )
        return None

    def classify_farms(self, farms: List[FarmData]) -> List[FarmData]:
        """
        Classify multiple farms.

        Applies classification to each farm in the list and updates the
        'group' attribute. Farms that cannot be classified will have
        group=None.

        Args:
            farms: List of FarmData objects to classify

        Returns:
            List of FarmData objects with group attribute set

        Note:
            This method modifies the input FarmData objects in place
            by setting their 'group' attribute.
        """
        classified_count = 0
        unclassified_count = 0

        for farm in farms:
            group = self.classify_farm(farm)
            farm.group = group

            if group is not None:
                classified_count += 1
            else:
                unclassified_count += 1

        logger.info(
            f"Classification complete: {classified_count} classified, "
            f"{unclassified_count} unclassified out of {len(farms)} total farms"
        )

        return farms

    def get_profile_for_group(self, group: FarmGroup) -> Optional[GroupProfile]:
        """
        Get the profile definition for a specific group.

        Args:
            group: FarmGroup to get profile for

        Returns:
            GroupProfile if found, None otherwise
        """
        for profile in self.profiles:
            if profile.group_name == group:
                return profile
        return None

    def get_all_profiles(self) -> List[GroupProfile]:
        """
        Get all defined group profiles.

        Returns:
            List of all GroupProfile objects
        """
        return self.profiles.copy()
