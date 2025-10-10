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

    def __init__(self, use_six_indicators: Optional[bool] = None) -> None:
        """
        Initialize the classifier with predefined group profiles.

        Args:
            use_six_indicators: If True, use 6 indicators (including slaughter fields).
                               If False, use 4 indicators only (ignoring slaughter fields).
                               If None, use configuration setting.
        """
        if use_six_indicators is None:
            config = get_config()
            use_six_indicators = config.classification.use_six_indicators

        self.use_six_indicators = use_six_indicators
        self.profiles: List[GroupProfile] = self._create_profiles(use_six_indicators)
        indicator_mode = "6 indicators" if use_six_indicators else "4 indicators"
        logger.info(
            f"Classifier initialized with {len(self.profiles)} group profiles ({indicator_mode})"
        )

    @staticmethod
    def _create_profiles(use_six_indicators: bool = True) -> List[GroupProfile]:
        """
        Create the lookup table of farm group profiles.

        Each profile defines the expected binary pattern for classification.

        Args:
            use_six_indicators: If True, uses all 6 indicators (NEW classification).
                               If False, uses only 4 indicators (OLD classification).

        Returns:
            List of GroupProfile objects defining each farm group

        Note:
            The order of profiles matters for classification priority.
            More specific patterns should come before more general ones.

            NEW Patterns (6 fields):
            - Muku:       [0, 0, 0, 0, 0, 1]
            - Muku_Amme:  [0, 0, 1, 0, 0, 1]
            - Milchvieh:  [1, 0, 0, 1, (0||1), (0||1)] - accepts any value for fields 5&6
            - BKMmZ:      [1, 0, 1, 0, 0, 1]
            - BKMoZ:      [1, 0, 0, 0, 0, 1]
            - IKM:        [0, 1, 1, 0, 0, 1]

            OLD Patterns (4 fields, ignoring slaughter indicators):
            - Muku:       [0, 0, 0, 0, *, *]
            - Muku_Amme:  [0, 0, 1, 0, *, *]
            - Milchvieh:  [1, 0, 0, 1, *, *]
            - BKMmZ:      [1, 0, 1, 0, *, *]
            - BKMoZ:      [1, 0, 0, 0, *, *]
            - IKM:        [0, 1, 1, 0, *, *]
        """
        if use_six_indicators:
            # NEW: 6-indicator classification (with slaughter fields)
            profiles = [
                # Muku: Mother cow farms without nurse cows
                # Pattern: [0, 0, 0, 0, 0, 1]
                GroupProfile(
                    group_name=FarmGroup.MUKU,
                    female_dairy_cattle=0,
                    female_cattle=0,
                    calf_arrivals=0,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=0,
                    young_slaughterings=1,
                ),
                # Muku_Amme: Mother cow farms with nurse cows
                # Pattern: [0, 0, 1, 0, 0, 1]
                GroupProfile(
                    group_name=FarmGroup.MUKU_AMME,
                    female_dairy_cattle=0,
                    female_cattle=0,
                    calf_arrivals=1,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=0,
                    young_slaughterings=1,
                ),
                # Milchvieh: Dairy farms
                # Pattern: [1, 0, 0, 1, (0||1), (0||1)] - accepts any value for fields 5&6
                # Using None to match any value for female_slaughterings and young_slaughterings
                GroupProfile(
                    group_name=FarmGroup.MILCHVIEH,
                    female_dairy_cattle=1,
                    female_cattle=0,
                    calf_arrivals=0,
                    calf_non_slaughter_leavings=1,
                    female_slaughterings=None,  # Accepts 0 or 1
                    young_slaughterings=None,  # Accepts 0 or 1
                ),
                # BKMmZ: Combined keeping dairy with breeding
                # Pattern: [1, 0, 1, 0, 0, 1]
                GroupProfile(
                    group_name=FarmGroup.BKMMZ,
                    female_dairy_cattle=1,
                    female_cattle=0,
                    calf_arrivals=1,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=0,
                    young_slaughterings=1,
                ),
                # BKMoZ: Combined keeping dairy without breeding
                # Pattern: [1, 0, 0, 0, 0, 1]
                GroupProfile(
                    group_name=FarmGroup.BKMOZ,
                    female_dairy_cattle=1,
                    female_cattle=0,
                    calf_arrivals=0,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=0,
                    young_slaughterings=1,
                ),
                # IKM: Intensive calf rearing
                # Pattern: [0, 1, 1, 0, 0, 1]
                GroupProfile(
                    group_name=FarmGroup.IKM,
                    female_dairy_cattle=0,
                    female_cattle=1,
                    calf_arrivals=1,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=0,
                    young_slaughterings=1,
                ),
            ]
        else:
            # OLD: 4-indicator classification (ignoring slaughter fields)
            # Use None for slaughter fields to accept any value
            profiles = [
                # Muku: Mother cow farms without nurse cows
                # Pattern: [0, 0, 0, 0, *, *]
                GroupProfile(
                    group_name=FarmGroup.MUKU,
                    female_dairy_cattle=0,
                    female_cattle=0,
                    calf_arrivals=0,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=None,  # Ignore
                    young_slaughterings=None,  # Ignore
                ),
                # Muku_Amme: Mother cow farms with nurse cows
                # Pattern: [0, 0, 1, 0, *, *]
                GroupProfile(
                    group_name=FarmGroup.MUKU_AMME,
                    female_dairy_cattle=0,
                    female_cattle=0,
                    calf_arrivals=1,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=None,  # Ignore
                    young_slaughterings=None,  # Ignore
                ),
                # Milchvieh: Dairy farms
                # Pattern: [1, 0, 0, 1, *, *]
                GroupProfile(
                    group_name=FarmGroup.MILCHVIEH,
                    female_dairy_cattle=1,
                    female_cattle=0,
                    calf_arrivals=0,
                    calf_non_slaughter_leavings=1,
                    female_slaughterings=None,  # Ignore
                    young_slaughterings=None,  # Ignore
                ),
                # BKMmZ: Combined keeping dairy with breeding
                # Pattern: [1, 0, 1, 0, *, *]
                GroupProfile(
                    group_name=FarmGroup.BKMMZ,
                    female_dairy_cattle=1,
                    female_cattle=0,
                    calf_arrivals=1,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=None,  # Ignore
                    young_slaughterings=None,  # Ignore
                ),
                # BKMoZ: Combined keeping dairy without breeding
                # Pattern: [1, 0, 0, 0, *, *]
                GroupProfile(
                    group_name=FarmGroup.BKMOZ,
                    female_dairy_cattle=1,
                    female_cattle=0,
                    calf_arrivals=0,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=None,  # Ignore
                    young_slaughterings=None,  # Ignore
                ),
                # IKM: Intensive calf rearing
                # Pattern: [0, 1, 1, 0, *, *]
                GroupProfile(
                    group_name=FarmGroup.IKM,
                    female_dairy_cattle=0,
                    female_cattle=1,
                    calf_arrivals=1,
                    calf_non_slaughter_leavings=0,
                    female_slaughterings=None,  # Ignore
                    young_slaughterings=None,  # Ignore
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
                female_slaughter=farm.indicator_female_slaughterings,
                young_slaughter=farm.indicator_young_slaughterings,
            ):
                logger.debug(
                    f"Farm {farm.tvd} classified as {profile.group_name.value} "
                    f"[{farm.indicator_female_dairy_cattle_v2}, "
                    f"{farm.indicator_female_cattle}, "
                    f"{farm.indicator_calf_arrivals}, "
                    f"{farm.indicator_calf_leavings}, "
                    f"{farm.indicator_female_slaughterings}, "
                    f"{farm.indicator_young_slaughterings}]"
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
                f"{farm.indicator_calf_leavings}, "
                f"{farm.indicator_female_slaughterings}, "
                f"{farm.indicator_young_slaughterings}]"
            )
        else:
            logger.debug(
                f"Farm {farm.tvd} could not be classified. Pattern: "
                f"[{farm.indicator_female_dairy_cattle_v2}, "
                f"{farm.indicator_female_cattle}, "
                f"{farm.indicator_calf_arrivals}, "
                f"{farm.indicator_calf_leavings}, "
                f"{farm.indicator_female_slaughterings}, "
                f"{farm.indicator_young_slaughterings}]"
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
