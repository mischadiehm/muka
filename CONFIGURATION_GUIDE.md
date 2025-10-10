# Configuration System Guide

## Overview

The MuKa analysis project uses a **centralized configuration system** built on Pydantic v2 and pydantic-settings. This provides type-safe, validated configuration with multiple loading sources and clear priorities.

## Key Features

- ✅ **Type-safe configuration** - All settings validated with Pydantic v2
- ✅ **Multiple sources** - Environment variables, TOML files, defaults
- ✅ **Clear priority** - Env vars > Config file > Defaults
- ✅ **Validation** - Invalid values caught at startup
- ✅ **Single source of truth** - All configuration in one place
- ✅ **Easy access** - Global singleton pattern with `get_config()`

## Configuration Structure

The configuration is organized into logical sections:

```python
AppConfig
├── paths              # File and directory paths
├── classification     # Classification parameters
├── analysis           # Statistical analysis settings
├── validation         # Data validation rules
├── output             # Output formatting and display
└── logging            # Logging configuration
```

## Basic Usage

### Getting Configuration

```python
from muka_analysis.config import get_config

# Get global configuration instance
config = get_config()

# Access configuration values
csv_dir = config.paths.csv_dir
output_dir = config.paths.output_dir
theme = config.output.default_theme
min_group_size = config.analysis.min_group_size
```

### Initializing Configuration

```python
from muka_analysis.config import init_config
from pathlib import Path

# Initialize with defaults
config = init_config()

# Initialize with custom config file
config = init_config(Path("custom_config.toml"))

# Force reinitialization
config = init_config(force=True)
```

### Using Configuration in Code

```python
from muka_analysis.config import get_config
import logging

logger = logging.getLogger(__name__)

def process_data():
    config = get_config()
    
    # Get paths
    input_path = config.paths.get_default_input_path()
    output_path = config.paths.get_classified_output_path()
    
    # Use configuration parameters
    if config.classification.require_all_fields:
        # Validate all fields
        pass
    
    # Use analysis settings
    min_size = config.analysis.min_group_size
    logger.info(f"Minimum group size: {min_size}")
```

## Configuration Sources

### 1. Default Values (Lowest Priority)

Built-in defaults defined in `muka_analysis/config.py`:

```python
PathsConfig(
    csv_dir=Path("csv"),
    output_dir=Path("output"),
    ...
)
```

### 2. Configuration File (Medium Priority)

Create `muka_config.toml` in your project root:

```toml
[paths]
csv_dir = "custom_data"
output_dir = "custom_output"

[analysis]
min_group_size = 10
confidence_level = 0.99

[output]
default_theme = "light"
show_progress = true
```

**Example file:** See `muka_config.example.toml` for a complete template.

### 3. Environment Variables (Highest Priority)

Override any setting with environment variables:

```bash
# Format: MUKA_<SECTION>__<SETTING>
export MUKA_DEBUG=true
export MUKA_PATHS__CSV_DIR=/custom/data
export MUKA_PATHS__OUTPUT_DIR=/custom/output
export MUKA_CLASSIFICATION__PRESENCE_THRESHOLD=0.5
export MUKA_ANALYSIS__MIN_GROUP_SIZE=10
export MUKA_OUTPUT__DEFAULT_THEME=light
export MUKA_LOGGING__CONSOLE_LEVEL=DEBUG
```

**Note:** Use `__` (double underscore) for nested configuration.

## Configuration Sections

### Paths Configuration

File and directory paths:

```python
config.paths.csv_dir                    # Input CSV directory
config.paths.output_dir                 # Output directory
config.paths.log_file                   # Log file path
config.paths.default_input_file         # Default input filename
config.paths.classified_output_file     # Classified output filename
config.paths.summary_output_file        # Summary Excel filename

# Helper methods
config.paths.get_default_input_path()       # Full path to default input
config.paths.get_classified_output_path()   # Full path to classified output
config.paths.get_summary_output_path()      # Full path to summary output
```

### Classification Configuration

Farm classification parameters:

```python
config.classification.presence_threshold            # Binary threshold (>0 = present)
config.classification.require_all_fields            # Require all fields present
config.classification.allow_missing_values          # Allow missing values
config.classification.show_unclassified_warnings    # Show warnings for unclassified farms (default: False)
```

**Note:** By default, warnings for unclassified farms are hidden. Enable with `--show-unclassified-warnings` flag or set `MUKA_CLASSIFICATION__SHOW_UNCLASSIFIED_WARNINGS=true`.

### Analysis Configuration

Statistical analysis settings:

```python
config.analysis.confidence_level    # Confidence level (0.0-1.0)
config.analysis.percentiles         # Percentiles to calculate [0.25, 0.50, 0.75]
config.analysis.min_group_size      # Minimum farms in group for reporting
```

### Validation Configuration

Data validation rules:

```python
config.validation.balance_tolerance_pct     # Tolerance % for balance checks
config.validation.min_year                  # Minimum valid year
config.validation.max_year                  # Maximum valid year
config.validation.min_tvd                   # Minimum valid TVD number
```

### Output Configuration

Output formatting and display:

```python
config.output.csv_encoding          # CSV encoding
config.output.csv_separator         # CSV separator
config.output.decimal_places        # Decimal places in output
config.output.max_display_rows      # Max rows in console
config.output.show_progress         # Show progress bars
config.output.default_theme         # Color theme (dark/light/auto)
```

### Logging Configuration

Logging behavior:

```python
config.logging.console_level        # Console log level
config.logging.file_level           # File log level
config.logging.show_timestamps      # Show timestamps
config.logging.show_module_names    # Show module names
```

## Integration with CLI

The CLI automatically uses configuration for defaults:

```python
import typer
from typing import Annotated, Optional
from pathlib import Path
from muka_analysis.config import get_config

app = typer.Typer()

@app.command()
def analyze(
    input_file: Annotated[
        Optional[Path],
        typer.Option("--input", "-i")
    ] = None,
) -> None:
    """Analyze farm data."""
    config = get_config()
    
    # Use config default if not provided
    if input_file is None:
        input_file = config.paths.get_default_input_path()
    
    # Use other config values
    output_dir = config.paths.output_dir
    show_progress = config.output.show_progress
```

## Validation and Type Safety

All configuration values are validated at load time:

```python
# ✅ Valid configuration
config.analysis.confidence_level = 0.95  # Float between 0 and 1
config.analysis.min_group_size = 10      # Integer >= 1
config.output.default_theme = "dark"     # Must be "dark", "light", or "auto"

# ❌ Invalid configuration (raises ValidationError)
config.analysis.confidence_level = 1.5   # Error: Must be <= 1.0
config.analysis.min_group_size = 0       # Error: Must be >= 1
config.output.default_theme = "blue"     # Error: Invalid theme
```

## Testing with Configuration

### Mock Configuration in Tests

```python
import pytest
from muka_analysis.config import init_config, reset_config, AppConfig

def test_with_custom_config():
    # Reset global config
    reset_config()
    
    # Create custom config
    config = init_config()
    config.analysis.min_group_size = 5
    
    # Run tests with this config
    result = my_function()
    
    # Clean up
    reset_config()

@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    reset_config()
    config = init_config()
    yield config
    reset_config()
```

### Temporary Environment Variables

```python
import os
import pytest

@pytest.fixture
def custom_env(monkeypatch):
    """Set custom environment variables for testing."""
    monkeypatch.setenv("MUKA_DEBUG", "true")
    monkeypatch.setenv("MUKA_ANALYSIS__MIN_GROUP_SIZE", "5")
    yield
```

## Configuration Display

### Show Configuration Summary

```python
from muka_analysis.config import get_config
from muka_analysis.output import get_output

config = get_config()
output = get_output()

# Display configuration summary
summary = config.summary()
output.show_summary("Configuration", summary)
```

### Export Full Configuration

```python
config = get_config()

# Export as dictionary
config_dict = config.to_dict()

# Save to file (manual)
import json
with open("config_export.json", "w") as f:
    json.dump(config_dict, f, indent=2)
```

## Best Practices

### ✅ DO

- **Use `get_config()`** for accessing configuration throughout the app
- **Initialize once** at application startup with `init_config()`
- **Use environment variables** for deployment-specific settings
- **Use config file** for project-specific defaults
- **Validate early** - Load config at startup to catch errors
- **Document changes** when adding new configuration options

### ❌ DON'T

- **Don't hardcode values** - Add them to config instead
- **Don't create multiple configs** - Use the global instance
- **Don't mutate config** at runtime (except for testing)
- **Don't bypass validation** - Use Pydantic models
- **Don't use magic strings** - Access via config object

## Adding New Configuration

To add a new configuration option:

1. **Add to appropriate config model:**

```python
# In muka_analysis/config.py
class AnalysisConfig(BaseModel):
    # ... existing fields ...
    
    new_parameter: float = Field(
        default=1.0,
        ge=0.0,
        description="Description of new parameter",
    )
```

2. **Add to example config file:**

```toml
# In muka_config.example.toml
[analysis]
new_parameter = 1.0  # Description
```

3. **Update documentation:**
   - Add to this guide
   - Add to docstrings
   - Update Copilot instructions if relevant

4. **Use in code:**

```python
config = get_config()
value = config.analysis.new_parameter
```

## Troubleshooting

### Configuration Not Loading

```python
from muka_analysis.config import get_config, init_config

# Force reload
config = init_config(force=True)

# Check configuration
print(config.summary())
```

### Environment Variables Not Working

```bash
# Check variable is set
echo $MUKA_DEBUG

# Use correct format with double underscore
export MUKA_PATHS__CSV_DIR=/custom/path  # ✅
export MUKA_PATHS_CSV_DIR=/custom/path   # ❌ Wrong separator
```

### Validation Errors

```python
# Check validation errors
try:
    config = init_config()
except Exception as e:
    print(f"Configuration error: {e}")
    # Fix the invalid configuration
```

## Examples

### Example 1: Development Setup

```bash
# Use defaults for development
export MUKA_DEBUG=true
export MUKA_LOGGING__CONSOLE_LEVEL=DEBUG
export MUKA_OUTPUT__SHOW_PROGRESS=true
```

### Example 2: Production Setup

```bash
# Production configuration
export MUKA_DEBUG=false
export MUKA_PATHS__CSV_DIR=/data/muka/input
export MUKA_PATHS__OUTPUT_DIR=/data/muka/output
export MUKA_LOGGING__CONSOLE_LEVEL=INFO
export MUKA_LOGGING__FILE_LEVEL=WARNING
```

### Example 3: Custom Analysis

```toml
# custom_analysis.toml
[analysis]
min_group_size = 50
confidence_level = 0.99
percentiles = [0.10, 0.25, 0.50, 0.75, 0.90]

[output]
decimal_places = 4
```

```python
from muka_analysis.config import init_config
from pathlib import Path

config = init_config(Path("custom_analysis.toml"))
```

## Related Documentation

- **Output Interface:** See `OUTPUT_INTERFACE_GUIDE.md`
- **API Reference:** See `muka_analysis/config.py`
- **Examples:** See `muka_config.example.toml`
- **Copilot Instructions:** See `.github/copilot-instructions.md`
