# GitHub Copilot Instructions for CSV Data Processing Project

## Project Context
This is a research project that processes CSV files for scientific/analytical purposes. **Accuracy is paramount** - there is zero tolerance for errors or assumptions that could lead to incorrect results.

## CRITICAL: NO SUMMARY FILES
- **NEVER** create summary, changelog, or completion markdown files
- **NEVER** create files like "CONFIGURATION_COMPLETE.md", "FEATURE_SUMMARY.md", etc.
- **ONLY** update existing documentation files (README.md, USAGE.md, etc.)
- **EXPLANATION:** These summary files clutter the repository and become outdated
- **EXAMPLES:**
  - ❌ CONFIGURATION_COMPLETE.md
  - ❌ ANALYSIS_OUTPUT_IMPROVEMENTS.md
  - ❌ FEATURE_IMPLEMENTATION_SUMMARY.md
  - ❌ CHANGES_SUMMARY.md
  - ✅ Update README.md instead
  - ✅ Update relevant guide (CONFIGURATION_GUIDE.md, OUTPUT_INTERFACE_GUIDE.md, etc.)
- **REMEMBER:** Commit messages and git history are for tracking changes, not markdown files

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

## CRITICAL: Configuration Management
- **THIS PROJECT USES CENTRALIZED CONFIGURATION**
- **ALWAYS** use `get_config()` to access configuration values
- **NEVER** hardcode paths, thresholds, or other configurable values
- **EXAMPLES:**
  - ✅ `config = get_config(); path = config.paths.csv_dir`
  - ✅ `threshold = get_config().classification.presence_threshold`
  - ❌ `path = Path("csv")`
  - ❌ `threshold = 0.0`
- **CONFIGURATION:** Can be set via env vars (MUKA_*), config file, or defaults
- **REMEMBER:** Configuration is validated at load time with Pydantic v2

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

### 9. Configuration Management Best Practices

#### Centralized Configuration
- **ALWAYS** use `AppConfig` for ALL configurable values
- **NEVER** hardcode paths, thresholds, or parameters
- **ACCESS** via `get_config()` or pass config to functions
- **INITIALIZE** at application start with `init_config()`

#### Configuration Best Practices
- **NEVER** hardcode what can be configured
- **USE** `get_config()` consistently throughout codebase
- **VALIDATE** configuration at startup (automatic with Pydantic)
- **DOCUMENT** new configuration options clearly
- **PROVIDE** sensible defaults for all settings
- **TEST** with different configuration values

### 10. Output Interface Best Practices

#### Centralized Output Management
- **ALWAYS** use `OutputInterface` for ALL console output, logging, and user interactions
- **NEVER** use `print()`, `console.print()`, or direct Rich calls
- **INITIALIZE** output interface at application start with theme and verbosity settings
- **ACCESS** via `get_output()` or pass as parameter to functions

## CRITICAL REMINDERS
1. **NEVER** assume data format - always validate
2. **NEVER** use magic numbers - define constants
3. **NEVER** ignore edge cases
4. **ALWAYS** ask for clarification when uncertain
5. **ALWAYS** validate calculations against known examples
6. **RESEARCH PROJECT** - accuracy over performance
