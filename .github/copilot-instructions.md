# GitHub Copilot Instructions for CSV Data Processing Project

## Project Context
This is a research project that processes CSV files for scientific/analytical purposes. **Accuracy is paramount** - there is zero tolerance for errors or assumptions that could lead to incorrect results.

## CRITICAL: Environment Setup
- **THIS PROJECT USES UV FOR PACKAGE MANAGEMENT**
- **ALWAYS** run Python commands with `uv run python` prefix
- **NEVER** use plain `python` or `/bin/python3` directly
- **EXAMPLES:**
  - ✅ `uv run python -m muka_analysis.main`
  - ✅ `uv run python script.py`
  - ✅ `uv run pytest`
  - ❌ `python -m muka_analysis.main`
  - ❌ `/bin/python3 script.py`
- **PACKAGE INSTALLATION:** Use `uv add <package>` not `pip install`
- **REMEMBER:** uv manages the virtual environment automatically

## Core Requirements

### 1. Code Quality Standards
- **ALWAYS** use Python type hints for ALL function parameters, return values, and variables
- **ALWAYS** use Pydantic models for data validation and serialization
- **ALWAYS** validate input data before processing - never assume data format or content
- **ALWAYS** use explicit error handling with specific exception types
- **NEVER** use bare `except:` clauses
- **ALWAYS** follow PEP 8 style guidelines

### 2. Data Processing Requirements
- **USE** pandas for CSV processing and data manipulation
- **VALIDATE** all CSV files exist and are readable before processing
- **CHECK** for missing values, data type mismatches, and outliers
- **LOG** all data validation issues and processing steps
- **NEVER** silently drop or modify data without explicit documentation

### 3. Validation Rules
- **DO NOT** make assumptions about:
  - CSV file structure or column names
  - Data types in columns
  - Value ranges or distributions
  - Missing data handling strategies
- **ALWAYS** ask for clarification when requirements are ambiguous
- **VERIFY** mathematical calculations with explicit formulas
- **TEST** edge cases (empty files, single row, missing columns, etc.)

### 4. Code Structure
- **USE** Pydantic v2 BaseModel for all data structures (with Field, model_validate, model_dump)
- **IMPLEMENT** proper separation of concerns:
  - Models: Data structure definitions with Pydantic v2
  - Validators: Input validation logic
  - Processors: Business logic and calculations
  - Utils: File I/O and helper functions
  - CLI: Modern command-line interface with Typer and Rich
- **CREATE** unit tests for every function that processes data
- **USE** Rich for all console output (tables, progress bars, error messages)
- **USE** Typer for CLI commands with proper type hints and documentation
- **DOCUMENT** all functions with docstrings including:
  - Parameters with types
  - Return values with types
  - Possible exceptions
  - Example usage

### 5. Dependencies
- **PREFER** standard library when possible
- **USE** established libraries:
  - pandas for data processing
  - pydantic v2 for data validation (BaseModel, Field, model_validate, model_dump)
  - numpy for numerical operations (when needed)  
  - rich for console output, tables, progress bars, and error display
  - typer for CLI interface with type hints and automatic help generation
  - pytest for testing
- **AVOID** unnecessary dependencies

### 6. Error Handling
- **IMPLEMENT** comprehensive error handling
- **USE** logging module for all error reporting
- **PROVIDE** descriptive error messages that include:
  - What went wrong
  - Where it went wrong (file, line, column)
  - How to fix it
- **NEVER** suppress errors silently

### 7. Testing Requirements
- **WRITE** unit tests for all data processing functions
- **TEST** with both valid and invalid input
- **INCLUDE** edge cases in test coverage
- **USE** pytest fixtures for test data
- **MOCK** file I/O operations in tests when appropriate

### 8. Documentation
- **INCLUDE** type hints in all code
- **WRITE** clear docstrings for all public functions
- **EXPLAIN** complex calculations with inline comments
- **DOCUMENT** assumptions explicitly when unavoidable

### 9. Output Interface Best Practices

#### Centralized Output Management
- **ALWAYS** use `OutputInterface` for ALL console output, logging, and user interactions
- **NEVER** use `print()`, `console.print()`, or direct Rich calls
- **INITIALIZE** output interface at application start with theme and verbosity settings
- **ACCESS** via `get_output()` or pass as parameter to functions

#### Output Interface Usage
```python
from muka_analysis.output import init_output, ColorScheme

# Initialize with theme
output = init_output(color_scheme=ColorScheme.DARK, verbose=False)

# Success/error/warning/info messages
output.success("Operation completed!")
output.error("Something went wrong")
output.warning("Please review this")
output.info("Processing data...")

# User interaction
if output.confirm("Continue with operation?"):
    value = output.prompt("Enter value:", default="100")

# Display data
output.show_summary("Results", {"Total": 100, "Success": 95})

# Progress tracking
with output.simple_progress() as progress:
    task = progress.add_task("Processing...", total=None)
    # Do work
    progress.update(task, description="✓ Complete")

# Section headers
output.section("Data Analysis")
```

#### Theme and Color Management
- **USE** centralized color scheme definitions (dark/light/auto)
- **SUPPORT** theme switching via CLI flag `--theme dark|light|auto`
- **DEFINE** colors in `ThemeColors` model, not inline
- **ALLOW** easy theme extension for custom color schemes

#### Logging Through Output Interface
- **CONFIGURE** logging automatically via `OutputInterface`
- **USE** standard Python logging (logger.info, logger.error, etc.)
- **OUTPUT** logs through Rich handler with consistent styling
- **FILE** logging configured automatically alongside console

#### Rich and Typer Integration
- **USE** Typer for all CLI interfaces with proper type annotations
- **IMPLEMENT** command groups for different functionalities
- **PROVIDE** comprehensive help text and examples
- **USE** `Annotated` types for parameter documentation
- **VALIDATE** file paths with Typer's built-in path validation
- **IMPLEMENT** confirmation prompts via OutputInterface

#### CLI Command Structure with Output Interface
```python
@app.command()
def command_name(
    required_param: Annotated[Path, typer.Argument(help="Description")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    theme: Annotated[ColorScheme, typer.Option("--theme", "-t")] = ColorScheme.DARK,
) -> None:
    """Command description with examples."""
    output = init_output(color_scheme=theme, verbose=verbose)
    logger = logging.getLogger(__name__)
    
    try:
        output.section("Operation Name")
        # Do work
        output.success("Completed!")
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        output.error(f"Operation failed: {e}")
        raise typer.Exit(1)
```

## Example Code Templates

### Pydantic v2 Model Template
```python
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)

class DataRecord(BaseModel):
    """Validated data record from CSV."""
    field_name: str = Field(..., description="Description of field")
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        """Validate field_name meets requirements."""
        if not v:
            raise ValueError("field_name cannot be empty")
        return v
```

### Output Interface Usage Template
```python
from typing import List, Dict, Any
from pathlib import Path
from muka_analysis.output import OutputInterface, ColorScheme, init_output
import logging

logger = logging.getLogger(__name__)

def display_results(output: OutputInterface, data: List[Dict[str, Any]]) -> None:
    """Display results using output interface."""
    # Create custom table
    table = output.create_table(
        "Results",
        [("Metric", "data"), ("Value", "highlight")]
    )
    
    for item in data:
        table.add_row(item["metric"], str(item["value"]))
    
    output.show_table(table)
    
    # Or use built-in summary
    summary_dict = {item["metric"]: item["value"] for item in data}
    output.show_summary("Results", summary_dict)

def process_with_progress(output: OutputInterface) -> None:
    """Process data with progress indicator."""
    with output.simple_progress() as progress:
        task = progress.add_task("Processing...", total=None)
        # Do work here
        progress.update(task, description="✓ Complete")
    
    output.success("Processing completed!")

def interactive_operation(output: OutputInterface) -> None:
    """Perform operation with user confirmation."""
    output.section("Data Processing")
    
    if output.confirm("Start processing?"):
        with output.simple_progress() as progress:
            task = progress.add_task("Working...", total=None)
            # Process data
            progress.update(task, description="✓ Done")
        
        output.success("Operation completed!")
    else:
        output.warning("Operation cancelled by user")
```

### Typer CLI with Output Interface Template
```python
import typer
import logging
from typing import Annotated, Optional
from pathlib import Path
from muka_analysis.output import init_output, ColorScheme

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="tool-name",
    help="Tool description",
    rich_markup_mode="rich",
)

@app.command()
def process(
    input_file: Annotated[
        Path,
        typer.Argument(help="Input CSV file path", exists=True, readable=True)
    ],
    output_file: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file path")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
    theme: Annotated[
        ColorScheme,
        typer.Option("--theme", "-t", help="Color scheme: dark, light, or auto")
    ] = ColorScheme.DARK,
) -> None:
    """
    Process data with comprehensive validation.
    
    Example:
        [bold]tool-name process data.csv --output results.csv --theme dark[/bold]
    """
    # Initialize output interface with theme
    output = init_output(color_scheme=theme, verbose=verbose)
    
    try:
        output.section("Data Processing")
        output.info(f"Processing: {input_file}")
        
        # Process data here
        with output.simple_progress() as progress:
            task = progress.add_task("Processing...", total=None)
            # Do work
            progress.update(task, description="✓ Complete")
        
        output.success("Processing completed!")
        
        # Show summary
        output.show_summary("Results", {
            "Input": str(input_file),
            "Output": str(output_file),
            "Status": "Success"
        })
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        output.error(f"Error: {e}")
        raise typer.Exit(1)
```

### Error Handling Template
```python
def process_csv(file_path: Path) -> pd.DataFrame:
    """
    Process CSV file with validation.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Validated and processed DataFrame
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV data is invalid
        
    Example:
        >>> df = process_csv(Path("data.csv"))
    """
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        # Validate data here
        return df
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        raise
```

## CRITICAL REMINDERS
1. **NEVER** assume data format - always validate
2. **NEVER** use magic numbers - define constants
3. **NEVER** ignore edge cases
4. **ALWAYS** ask for clarification when uncertain
5. **ALWAYS** validate calculations against known examples
6. **RESEARCH PROJECT** - accuracy over performance
