# Output Interface Developer Guide

## Overview

The `OutputInterface` provides a centralized, theme-aware system for all console output, logging, and user interactions in the MuKa analysis project. It abstracts away direct Rich and logging calls, ensuring consistent styling and easy theme management.

## Key Principles

1. **Never use `print()` or direct Rich calls** - Always use `OutputInterface` methods
2. **Initialize once per command** - Create output interface at CLI command entry point
3. **Pass as parameter** - Pass output interface to functions that need it
4. **Theme support** - All commands should support `--theme` flag
5. **Logging integration** - Use standard `logging` module, configured automatically

## Quick Start

### Basic Usage

```python
from muka_analysis.output import init_output, ColorScheme
import logging

logger = logging.getLogger(__name__)

def my_function():
    # Initialize output interface with theme
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)
    
    # Display messages
    output.section("My Operation")
    output.info("Starting process...")
    
    try:
        # Do work
        output.success("Operation completed!")
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        output.error(f"Operation failed: {e}")
```

## Color Schemes

Three color schemes are available:

- **`ColorScheme.DARK`** (default): Optimized for dark terminals
- **`ColorScheme.LIGHT`**: Optimized for light terminals  
- **`ColorScheme.AUTO`**: Auto-detect system theme (currently defaults to dark)

Themes can be extended by modifying `OutputInterface.THEMES` dictionary.

## Output Methods

### Basic Messages

```python
output.success("Operation completed!")   # ✅ Green success message
output.error("Something failed!")        # ❌ Red error message
output.warning("Please review this")     # ⚠️  Yellow warning
output.info("Processing data...")        # ℹ️  Blue informational
output.data("Dataset: 1000 rows")        # Cyan data display
output.header("Section Title")           # Bold blue header
```

### Sections and Separators

```python
output.section("Data Analysis")          # 🐄 with header and separator
output.separator()                       # ========== line
output.separator(length=80)              # Custom length
```

### Tables

```python
# Create custom table
table = output.create_table(
    "Results",
    [("Column 1", "data"), ("Column 2", "highlight")]
)
table.add_row("Value 1", "Value 2")
output.show_table(table)

# Or use built-in summary
output.show_summary(
    "Summary Title",
    {
        "Metric 1": "Value 1",
        "Metric 2": "Value 2",
    },
    highlight_keys=["Metric 1"]  # Optional highlighting
)
```

### Progress Indicators

```python
# Simple progress (no bar)
with output.simple_progress() as progress:
    task = progress.add_task("Loading...", total=None)
    # Do work
    progress.update(task, description="✓ Complete")

# Full progress with bar
with output.progress_context() as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

### User Interaction

```python
# Confirmation
if output.confirm("Continue with operation?", default=False):
    # User confirmed
    pass

# Text input
value = output.prompt("Enter threshold:", default="100")

# File lists
files = [Path("file1.csv"), Path("file2.csv")]
output.show_file_list("Files to process:", files, style="warning")
```

## Integration with Typer CLI

All CLI commands should follow this pattern:

```python
import typer
import logging
from pathlib import Path
from typing import Annotated
from muka_analysis.output import init_output, ColorScheme

logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command()
def my_command(
    input_file: Annotated[Path, typer.Argument(...)],
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    theme: Annotated[
        ColorScheme,
        typer.Option("--theme", "-t", help="Color scheme: dark, light, or auto")
    ] = ColorScheme.DARK,
) -> None:
    """Command description."""
    # Initialize output interface
    output = init_output(color_scheme=theme, verbose=verbose)
    
    try:
        output.section("My Command")
        output.info(f"Processing: {input_file}")
        
        # Do work with progress
        with output.simple_progress() as progress:
            task = progress.add_task("Working...", total=None)
            # Process
            progress.update(task, description="✓ Done")
        
        output.success("Command completed!")
        
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        output.error(f"Error: {e}")
        raise typer.Exit(1)
```

## Logging Integration

The output interface automatically configures logging:

- **Console logging** via Rich handler with theme colors
- **File logging** to `muka_analysis.log`
- **Verbosity control** via `verbose` parameter
- **Rich tracebacks** for better error display

Use standard Python logging:

```python
import logging

logger = logging.getLogger(__name__)

# These will use Rich formatting automatically
logger.debug("Debug message")    # Only in verbose mode
logger.info("Info message")      # Always shown
logger.warning("Warning")        # With warning styling
logger.error("Error occurred")   # With error styling
```

## Theme Customization

To add a new theme or modify colors:

```python
from muka_analysis.output import OutputInterface, ThemeColors, ColorScheme

# Define new theme
custom_theme = ThemeColors(
    success="bright_green",
    error="bright_red",
    warning="orange",
    info="bright_blue",
    data="bright_cyan",
    highlight="bright_magenta",
    header="bold bright_blue",
    progress="bright_cyan",
)

# Add to themes dictionary
OutputInterface.THEMES[ColorScheme.CUSTOM] = custom_theme
```

## Best Practices

### ✅ DO

- Initialize output interface once per CLI command
- Pass output interface to functions as parameter
- Use appropriate message types (success, error, warning, info)
- Include progress indicators for long operations
- Use tables for structured data display
- Enable verbose mode for debugging

### ❌ DON'T

- Use `print()` statements
- Create multiple output interfaces
- Use direct Rich console calls
- Hardcode color values
- Ignore theme parameter in CLI commands
- Mix output methods (pick either table or summary)

## Testing

When testing functions that use output interface:

```python
import pytest
from muka_analysis.output import init_output, ColorScheme

def test_my_function():
    output = init_output(color_scheme=ColorScheme.DARK, verbose=False)
    
    # Test with output interface
    result = my_function(output)
    
    # Output will be visible during test if needed
    assert result is not None
```

## Migration Guide

### From `print()`:

```python
# Before
print("Processing complete")

# After
output.success("Processing complete")
```

### From direct Rich console:

```python
# Before
from rich.console import Console
console = Console()
console.print("[green]Success![/green]")

# After
output.success("Success!")
```

### From direct logging config:

```python
# Before
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

# After
# No need - OutputInterface handles this
output = init_output(color_scheme=ColorScheme.DARK, verbose=False)
```

## Examples

See `demo_output_interface.py` for comprehensive examples of all features.

## Support

For questions or issues with the output interface, refer to:
- Source code: `muka_analysis/output.py`
- CLI implementation: `muka_analysis/cli.py`
- Copilot instructions: `.github/copilot-instructions.md`
