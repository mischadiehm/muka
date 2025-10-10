# Unclassified Farm Warnings Configuration

## Overview

A new configuration option has been added to control the display of warnings for farms that cannot be classified. By default, these warnings are **hidden** to reduce noise in the output.

## Problem Solved

Previously, the analysis would show many warnings like:
```
WARNING  Farm 11944 could not be classified. Pattern: [1, 0, 1, 1]
```

These warnings could be overwhelming, especially with large datasets where many farms don't match any classification profile.

## Solution

### Default Behavior (Warnings Hidden)

By default, unclassified farm warnings are not shown. They are logged at DEBUG level instead, so they're only visible when verbose logging is enabled.

```bash
# No unclassified warnings shown
uv run python -m muka_analysis analyze
```

### Enabling Warnings

There are **three ways** to enable these warnings:

#### 1. Command-Line Flag

```bash
uv run python -m muka_analysis analyze --show-unclassified-warnings
```

#### 2. Environment Variable

```bash
export MUKA_CLASSIFICATION__SHOW_UNCLASSIFIED_WARNINGS=true
uv run python -m muka_analysis analyze
```

#### 3. Configuration File

Create or edit `muka_config.toml`:

```toml
[classification]
show_unclassified_warnings = true
```

Then run normally:

```bash
uv run python -m muka_analysis analyze
```

## Configuration Details

### Config Section
**Section:** `classification`  
**Setting:** `show_unclassified_warnings`  
**Type:** `bool`  
**Default:** `false`

### Access in Code

```python
from muka_analysis.config import get_config

config = get_config()
if config.classification.show_unclassified_warnings:
    # Show warning
    logger.warning(f"Farm {tvd} could not be classified")
else:
    # Only log at debug level
    logger.debug(f"Farm {tvd} could not be classified")
```

## Use Cases

### When to Keep Warnings Hidden (Default)

- **Normal analysis runs** - You just want the results
- **Production environments** - Reduce log noise
- **Large datasets** - Many unclassified farms would clutter output
- **Automated processing** - Warnings not actionable

### When to Enable Warnings

- **Debugging classification logic** - See which farms don't match
- **Data quality analysis** - Understand unclassified patterns
- **Profile development** - Finding gaps in classification rules
- **Troubleshooting** - Understanding why certain farms are unclassified

## Examples

### Example 1: Normal Analysis (Quiet)

```bash
uv run python -m muka_analysis analyze --force
```

**Output:** Clean output without unclassified warnings

### Example 2: Debugging Classification

```bash
uv run python -m muka_analysis analyze --show-unclassified-warnings --verbose
```

**Output:** Shows all warnings and debug information

### Example 3: Production with Environment Variable

```bash
# In production environment - warnings disabled by default
export MUKA_PATHS__CSV_DIR=/data/production/input
export MUKA_PATHS__OUTPUT_DIR=/data/production/output
# Warnings are off by default, no need to set anything

uv run python -m muka_analysis analyze
```

### Example 4: Development Environment

```bash
# In development - enable warnings to see classification issues
export MUKA_DEBUG=true
export MUKA_CLASSIFICATION__SHOW_UNCLASSIFIED_WARNINGS=true
export MUKA_LOGGING__CONSOLE_LEVEL=DEBUG

uv run python -m muka_analysis analyze
```

## Technical Implementation

### Files Modified

1. **`muka_analysis/config.py`**
   - Added `show_unclassified_warnings` field to `ClassificationConfig`

2. **`muka_analysis/classifier.py`**
   - Updated `classify_farm()` to check configuration
   - Warnings shown only if enabled, otherwise logged at DEBUG level

3. **`muka_analysis/cli.py`**
   - Added `--show-unclassified-warnings` CLI flag
   - Flag overrides configuration setting

4. **`muka_config.example.toml`**
   - Added example configuration with explanation

5. **`CONFIGURATION_GUIDE.md`**
   - Documented new configuration option

6. **`README.md`**
   - Added usage example

### Code Changes

**Before:**
```python
logger.warning(
    f"Farm {farm.tvd} could not be classified. Pattern: "
    f"[{farm.indicator_female_dairy_cattle_v2}, "
    f"{farm.indicator_female_cattle}, "
    f"{farm.indicator_calf_arrivals}, "
    f"{farm.indicator_calf_leavings}]"
)
```

**After:**
```python
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
```

## Testing

### Test 1: Default Behavior (Warnings Hidden)

```bash
uv run python -m muka_analysis analyze --force 2>&1 | grep -i "could not be classified"
# Output: (empty - no warnings)
```

### Test 2: With Flag Enabled

```bash
uv run python -m muka_analysis analyze --force --show-unclassified-warnings 2>&1 | grep -i "could not be classified" | head -5
# Output: Shows WARNING messages for unclassified farms
```

### Test 3: With Environment Variable

```bash
MUKA_CLASSIFICATION__SHOW_UNCLASSIFIED_WARNINGS=true uv run python -m muka_analysis analyze --force 2>&1 | grep -i "could not be classified" | head -3
# Output: Shows WARNING messages
```

## Benefits

✅ **Cleaner Output** - By default, no warning noise  
✅ **Configurable** - Enable when needed for debugging  
✅ **Flexible** - Three ways to control (CLI, env var, config file)  
✅ **Backward Compatible** - Existing scripts work without changes  
✅ **Production-Ready** - Sensible default for automated processing  
✅ **Debug-Friendly** - Easy to enable for troubleshooting  

## Summary

The `show_unclassified_warnings` configuration option provides fine-grained control over classification warning visibility. By defaulting to `false`, the system provides cleaner output for normal operations while still making it easy to enable detailed warnings when needed for debugging or analysis.

**Key Point:** Warnings are **hidden by default** and can be enabled via CLI flag, environment variable, or configuration file when needed.
