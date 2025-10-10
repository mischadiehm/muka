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

### 9. Rich and Typer Integration Best Practices

#### Rich Console Output
- **USE** Rich for ALL console output instead of plain print statements
- **IMPLEMENT** proper color coding and formatting:
  - `[green]` for success messages
  - `[red]` for errors and failures
  - `[yellow]` for warnings
  - `[blue]` for informational headers
  - `[cyan]` for data/metrics
- **CREATE** Rich tables for data presentation with proper column styling
- **USE** Rich progress bars for long-running operations
- **ENABLE** Rich tracebacks for better error debugging

#### Typer CLI Design
- **USE** Typer for all CLI interfaces with proper type annotations
- **IMPLEMENT** command groups for different functionalities
- **PROVIDE** comprehensive help text and examples
- **USE** `Annotated` types for parameter documentation
- **VALIDATE** file paths with Typer's built-in path validation
- **IMPLEMENT** confirmation prompts for destructive operations

#### CLI Command Structure
```python
@app.command()
def command_name(
    required_param: Annotated[Path, typer.Argument(help="Description")],
    optional_param: Annotated[Optional[str], typer.Option("--flag", help="Description")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Command description with examples."""
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

### Rich Console Output Template
```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def display_results(data: List[Dict[str, Any]]) -> None:
    """Display results in a formatted table."""
    table = Table(title="Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for item in data:
        table.add_row(item["metric"], str(item["value"]))
    
    console.print(table)

def process_with_progress() -> None:
    """Process data with progress indicator."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing...", total=None)
        # Do work here
        progress.update(task, description="✓ Complete")
```

### Typer CLI Template
```python
import typer
from typing import Annotated, Optional
from pathlib import Path
from rich.console import Console

console = Console()

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
) -> None:
    """
    Process data with comprehensive validation.
    
    Example:
        [bold]tool-name process data.csv --output results.csv[/bold]
    """
    try:
        console.print(f"[blue]Processing: {input_file}[/blue]")
        # Process data here
        console.print("[green]✅ Processing completed![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
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
