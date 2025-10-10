"""
MuKa Farm Classification and Analysis Package.

This package provides tools for classifying farms based on cattle types and movements,
and performing statistical analysis on the classified data.

Features:
- Modern CLI with Rich console output and Typer interface
- Pydantic v2 models for robust data validation
- Comprehensive error handling and logging
- Export capabilities to CSV and Excel formats
"""

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.config import AppConfig, get_config, init_config
from muka_analysis.models import FarmData, FarmGroup, GroupProfile
from muka_analysis.output import ColorScheme, OutputInterface, get_output, init_output
from muka_analysis.validators import DataValidator

__version__ = "0.1.0"

__all__ = [
    "FarmData",
    "FarmGroup",
    "GroupProfile",
    "FarmAnalyzer",
    "DataValidator",
    "FarmClassifier",
    "OutputInterface",
    "ColorScheme",
    "get_output",
    "init_output",
    "AppConfig",
    "get_config",
    "init_config",
]

# Import CLI for easy access
try:
    from muka_analysis.cli import app as cli_app

    __all__.append("cli_app")
except ImportError:
    # CLI dependencies not available
    pass
