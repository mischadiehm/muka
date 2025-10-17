"""
Central configuration management for MuKa farm analysis.

This module provides a centralized configuration system using Pydantic models
for validation. Configuration can be loaded from:
1. Environment variables (highest priority)
2. Configuration file (muka_config.toml)
3. Default values (lowest priority)

All configuration settings are validated and type-checked using Pydantic v2.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class PathsConfig(BaseModel):
    """Configuration for file and directory paths."""

    # Input/Output directories
    csv_dir: Path = Field(
        default=Path("csv"),
        description="Directory containing input CSV files",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Directory for output files",
    )
    log_file: Path = Field(
        default=Path("muka_analysis.log"),
        description="Path to log file",
    )

    # Default filenames
    default_input_file: str = Field(
        default="BetriebsFilter_Population_18_09_2025_guy_jr.csv",
        description="Default input CSV filename",
    )
    classified_output_file: str = Field(
        default="classified_farms.csv",
        description="Default classified output CSV filename",
    )
    summary_output_file: str = Field(
        default="analysis_summary.xlsx",
        description="Default summary Excel filename",
    )

    @field_validator("csv_dir", "output_dir", mode="before")
    @classmethod
    def resolve_path(cls, v: Any) -> Path:
        """Resolve path to absolute path."""
        if isinstance(v, str):
            v = Path(v)
        if not isinstance(v, Path):
            raise ValueError(f"Expected Path or str, got {type(v)}")
        return v

    def get_default_input_path(self) -> Path:
        """Get full path to default input file."""
        return self.csv_dir / self.default_input_file

    def get_classified_output_path(self) -> Path:
        """Get full path to classified output file."""
        return self.output_dir / self.classified_output_file

    def get_summary_output_path(self) -> Path:
        """Get full path to summary output file."""
        return self.output_dir / self.summary_output_file


class ClassificationConfig(BaseModel):
    """Configuration for farm classification parameters."""

    # Binary thresholds (value > 0 means presence)
    presence_threshold: float = Field(
        default=0.0,
        ge=0.0,
        description="Threshold for determining presence in binary classification",
    )

    # Classification criteria
    indicator_mode: str = Field(
        default="6-indicators",
        description=(
            "Indicator mode for classification:\n"
            "  - '6-indicators': Use all 6 indicators (NEW method, default)\n"
            "  - '4-indicators': Use only first 4 indicators (OLD method)\n"
            "  - '5-indicators': Use 5 indicators, ignore female_slaughterings (field 5)\n"
            "  - '5-indicators-flex': Use 5 indicators, Milchvieh accepts any young_slaughterings"
        ),
    )

    # Validation settings
    require_all_fields: bool = Field(
        default=True,
        description="Require all fields to be present in input data",
    )
    allow_missing_values: bool = Field(
        default=False,
        description="Allow missing values in non-critical fields",
    )

    # Warning settings
    show_unclassified_warnings: bool = Field(
        default=False,
        description="Show warnings for farms that could not be classified",
    )


class AnalysisConfig(BaseModel):
    """Configuration for statistical analysis parameters."""

    # Statistical parameters
    confidence_level: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Confidence level for statistical calculations",
    )

    # Percentiles to calculate
    percentiles: List[float] = Field(
        default=[0.25, 0.50, 0.75],
        description="Percentiles to calculate in summary statistics",
    )

    # Minimum group size for reporting
    min_group_size: int = Field(
        default=1,
        ge=1,
        description="Minimum number of farms in a group for reporting",
    )

    @field_validator("percentiles")
    @classmethod
    def validate_percentiles(cls, v: List[float]) -> List[float]:
        """Validate percentile values are between 0 and 1."""
        for p in v:
            if not 0 <= p <= 1:
                raise ValueError(f"Percentile {p} must be between 0 and 1")
        return sorted(v)


class ValidationConfig(BaseModel):
    """Configuration for data validation parameters."""

    # Tolerance settings
    balance_tolerance_pct: float = Field(
        default=1.0,
        ge=0.0,
        description="Tolerance percentage for balance validation",
    )

    # Field ranges (for data quality checks)
    min_year: int = Field(
        default=2000,
        description="Minimum valid year",
    )
    max_year: int = Field(
        default=2100,
        description="Maximum valid year",
    )
    min_tvd: int = Field(
        default=1,
        description="Minimum valid TVD number",
    )

    @field_validator("min_year", "max_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate year is reasonable."""
        if not 1900 <= v <= 2200:
            raise ValueError(f"Year {v} is outside reasonable range")
        return v


class OutputConfig(BaseModel):
    """Configuration for output formatting and display."""

    # Output format settings
    csv_encoding: str = Field(
        default="utf-8",
        description="Encoding for CSV files",
    )
    csv_separator: str = Field(
        default=",",
        description="Separator for CSV files",
    )
    decimal_places: int = Field(
        default=2,
        ge=0,
        description="Number of decimal places in output",
    )

    # Display settings
    max_display_rows: int = Field(
        default=20,
        ge=1,
        description="Maximum rows to display in console output",
    )
    show_progress: bool = Field(
        default=True,
        description="Show progress bars during processing",
    )

    # Theme settings
    default_theme: str = Field(
        default="dark",
        description="Default color theme (dark/light/auto)",
    )

    @field_validator("default_theme")
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """Validate theme is valid."""
        valid_themes = ["dark", "light", "auto"]
        if v.lower() not in valid_themes:
            raise ValueError(f"Theme must be one of: {valid_themes}")
        return v.lower()


class LoggingConfig(BaseModel):
    """Configuration for logging behavior."""

    # Logging levels
    console_level: str = Field(
        default="INFO",
        description="Logging level for console output",
    )
    file_level: str = Field(
        default="DEBUG",
        description="Logging level for file output",
    )

    # Format settings
    show_timestamps: bool = Field(
        default=True,
        description="Show timestamps in log output",
    )
    show_module_names: bool = Field(
        default=True,
        description="Show module names in log output",
    )

    @field_validator("console_level", "file_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v_upper


class AppConfig(BaseSettings):
    """
    Main application configuration with all subsections.

    This class aggregates all configuration sections and handles loading
    from environment variables and configuration files.

    Environment variables use prefix MUKA_ and nested structure with __:
    - MUKA_PATHS__CSV_DIR=/path/to/csv
    - MUKA_CLASSIFICATION__PRESENCE_THRESHOLD=0.5
    - MUKA_OUTPUT__DEFAULT_THEME=light
    """

    model_config = SettingsConfigDict(
        env_prefix="MUKA_",
        env_nested_delimiter="__",
        case_sensitive=False,
        toml_file="muka_config.toml",
    )

    # Configuration sections
    paths: PathsConfig = Field(default_factory=PathsConfig)
    classification: ClassificationConfig = Field(default_factory=ClassificationConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Application metadata
    app_name: str = Field(
        default="MuKa Farm Analysis",
        description="Application name",
    )
    version: str = Field(
        default="0.1.0",
        description="Application version",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """
        Customize settings sources to include TOML file.

        Priority (highest to lowest):
        1. Environment variables
        2. TOML configuration file
        3. Default values
        """
        from pydantic_settings import TomlConfigSettingsSource

        return (
            env_settings,
            TomlConfigSettingsSource(settings_cls),
            init_settings,
        )

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "AppConfig":
        """
        Load configuration from file and environment.

        Args:
            config_file: Optional path to configuration file (TOML format)

        Returns:
            Loaded configuration object

        Example:
            >>> config = AppConfig.load()
            >>> config = AppConfig.load(Path("custom_config.toml"))
        """
        if config_file and config_file.exists():
            logger.info(f"Loading configuration from {config_file}")
            # TODO: Implement TOML file loading when needed
            # For now, just use environment variables and defaults
        else:
            logger.debug("Using default configuration and environment variables")

        return cls()

    def ensure_directories(self) -> None:
        """
        Create necessary directories if they don't exist.

        This should be called during application initialization to ensure
        all required directories are present.
        """
        dirs_to_create = [
            self.paths.csv_dir,
            self.paths.output_dir,
        ]

        for directory in dirs_to_create:
            if not directory.exists():
                logger.info(f"Creating directory: {directory}")
                directory.mkdir(parents=True, exist_ok=True)
            else:
                logger.debug(f"Directory exists: {directory}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return self.model_dump()

    def summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for display.

        Returns:
            Simplified configuration summary
        """
        return {
            "Application": {
                "Name": self.app_name,
                "Version": self.version,
                "Debug": self.debug,
            },
            "Paths": {
                "CSV Directory": str(self.paths.csv_dir),
                "Output Directory": str(self.paths.output_dir),
                "Log File": str(self.paths.log_file),
            },
            "Classification": {
                "Presence Threshold": self.classification.presence_threshold,
                "Require All Fields": self.classification.require_all_fields,
            },
            "Analysis": {
                "Min Group Size": self.analysis.min_group_size,
                "Confidence Level": self.analysis.confidence_level,
            },
            "Output": {
                "Theme": self.output.default_theme,
                "Show Progress": self.output.show_progress,
                "Decimal Places": self.output.decimal_places,
            },
        }


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance.

    Returns:
        Global AppConfig instance

    Example:
        >>> from muka_analysis.config import get_config
        >>> config = get_config()
        >>> print(config.paths.csv_dir)
    """
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config


def init_config(config_file: Optional[Path] = None, force: bool = False) -> AppConfig:
    """
    Initialize or reinitialize the global configuration.

    Args:
        config_file: Optional path to configuration file
        force: Force reinitialization even if already initialized

    Returns:
        Initialized AppConfig instance

    Example:
        >>> from muka_analysis.config import init_config
        >>> config = init_config(Path("custom_config.toml"))
    """
    global _config
    if _config is None or force:
        _config = AppConfig.load(config_file)
        _config.ensure_directories()
        logger.info("Configuration initialized")
    return _config


def reset_config() -> None:
    """
    Reset the global configuration to None.

    Useful for testing or forcing reconfiguration.
    """
    global _config
    _config = None
    logger.debug("Configuration reset")
