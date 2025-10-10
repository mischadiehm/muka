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
- **USE** Pydantic BaseModel for all data structures
- **IMPLEMENT** proper separation of concerns:
  - Models: Data structure definitions with Pydantic
  - Validators: Input validation logic
  - Processors: Business logic and calculations
  - Utils: File I/O and helper functions
- **CREATE** unit tests for every function that processes data
- **DOCUMENT** all functions with docstrings including:
  - Parameters with types
  - Return values with types
  - Possible exceptions
  - Example usage

### 5. Dependencies
- **PREFER** standard library when possible
- **USE** established libraries:
  - pandas for data processing
  - pydantic for data validation
  - numpy for numerical operations (when needed)
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

## Example Code Template

```python
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, validator, Field
import logging

logger = logging.getLogger(__name__)

class DataRecord(BaseModel):
    """Validated data record from CSV."""
    field_name: str = Field(..., description="Description of field")
    
    @validator('field_name')
    def validate_field_name(cls, v: str) -> str:
        """Validate field_name meets requirements."""
        if not v:
            raise ValueError("field_name cannot be empty")
        return v

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
