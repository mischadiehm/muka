"""
MuKa Farm Classification and Analysis Package.

This package provides tools for classifying farms based on cattle types and movements,
and performing statistical analysis on the classified data.
"""

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.models import FarmData, FarmGroup, GroupProfile
from muka_analysis.validators import DataValidator

__version__ = "0.1.0"

__all__ = [
    "FarmData",
    "FarmGroup",
    "GroupProfile",
    "FarmAnalyzer",
    "DataValidator",
    "FarmClassifier",
]
