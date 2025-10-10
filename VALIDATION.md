# Validation System Documentation

## Overview

A flexible validation system has been added to compare classification results with reference data. The system allows you to easily add ad-hoc validation functions to verify the accuracy of the farm classification.

## Architecture

### Core Components

1. **`validation.py`** - Main validation module with:
   - `ValidationResult`: Pydantic model for validation results
   - `GroupComparison`: Model for group-by-group comparison
   - `ValidationSuite`: Extensible framework for validators

2. **Integration in `main.py`** - Validation runs automatically as Step 3:
   - Reads reference data from CSV
   - Analyzes reference group distribution
   - Runs all registered validators
   - Outputs results to logs and Excel

## Current Validators

### 1. Group Comparison Validator

Compares your classification results with the reference "group" column in the CSV.

**What it does:**
- Counts farms in each group from your classification
- Counts farms in each group from the reference data
- Calculates absolute and percentage differences
- Validates differences are within tolerance (default: 5%)

**Example Output:**
```
Group Comparison Validation: FAILED
Total farms - Predicted: 25940, Reference: 19589
Maximum difference: 293.53% (tolerance: 5.0%)

Group-by-group comparison:
  ✗ BKMmZ: Predicted=1460, Reference=371, Diff=+1089 (293.53%)
  ✗ BKMoZ: Predicted=3776, Reference=1554, Diff=+2222 (142.99%)
  ✓ IKM: Predicted=809, Reference=809, Diff=+0 (0.00%)
  ✗ Milchvieh: Predicted=12006, Reference=5655, Diff=+6351 (112.31%)
  ✗ Muku: Predicted=6069, Reference=8291, Diff=-2222 (26.80%)
  ✗ Muku_Amme: Predicted=1820, Reference=2909, Diff=-1089 (37.44%)
```

## Adding New Validators

The system is designed to be easily extensible. Here's how to add a new validation function:

### Step 1: Define Your Validation Function

```python
def validate_something(
    self,
    classified_farms: List[FarmData],
    reference_df: pd.DataFrame,
) -> ValidationResult:
    """
    Your validation logic here.
    
    Args:
        classified_farms: List of farms with your classifications
        reference_df: DataFrame with reference data
        
    Returns:
        ValidationResult with pass/fail and details
    """
    # Your validation logic
    passed = True  # or False based on your checks
    
    return ValidationResult(
        validation_name="your_validator_name",
        passed=passed,
        message="Your validation message",
        details={"key": "value"},  # Any additional data
        metrics={"metric1": 123.45}  # Numeric metrics
    )
```

### Step 2: Register the Validator

In `validation.py`, add to `_register_default_validators()`:

```python
def _register_default_validators(self) -> None:
    """Register default validation functions."""
    self.register_validator("group_comparison", self.validate_group_comparison)
    self.register_validator("your_validator_name", self.validate_something)  # Add this
```

### Example: Animal Count Validator

Here's a complete example of adding a validator to check if total animal counts match:

```python
def validate_animal_counts(
    self,
    classified_farms: List[FarmData],
    reference_df: pd.DataFrame,
    tolerance_pct: float = 5.0,
) -> ValidationResult:
    """
    Validate that total animal counts match between prediction and reference.
    
    Args:
        classified_farms: List of classified farms
        reference_df: Reference DataFrame
        tolerance_pct: Acceptable percentage difference
        
    Returns:
        ValidationResult
    """
    # Calculate predicted total
    predicted_total = sum(farm.n_animals_total for farm in classified_farms)
    
    # Calculate reference total
    if "n_animals_total" not in reference_df.columns:
        raise ValueError("Reference DataFrame missing 'n_animals_total' column")
    
    reference_total = reference_df["n_animals_total"].sum()
    
    # Calculate difference
    diff = predicted_total - reference_total
    diff_pct = abs(diff / reference_total * 100) if reference_total > 0 else 0
    
    # Check if passed
    passed = diff_pct <= tolerance_pct
    
    message = f"Animal Count Validation: {'PASSED' if passed else 'FAILED'}\n"
    message += f"Predicted total: {predicted_total:,}\n"
    message += f"Reference total: {reference_total:,}\n"
    message += f"Difference: {diff:+,} ({diff_pct:.2f}%)"
    
    return ValidationResult(
        validation_name="animal_counts",
        passed=passed,
        message=message,
        details={
            "predicted_total": predicted_total,
            "reference_total": reference_total,
            "difference": diff,
        },
        metrics={
            "difference_pct": diff_pct,
            "predicted_total": float(predicted_total),
            "reference_total": float(reference_total),
        },
    )
```

## Output

Validation results are logged and saved in two places:

1. **Console/Log Output**: Detailed validation messages during execution
2. **Excel File**: `output/analysis_summary.xlsx` contains a "Validation" sheet with:
   - Validation name
   - Pass/Fail status
   - Summary message
   - Numeric metrics

## Reference Data Analysis

The validation system also analyzes the reference "group" column to show:
- Total records
- Number of unique groups
- Missing/NA values
- Distribution of each group

This helps you understand what the reference data looks like before comparing.

## Key Features

✅ **Extensible**: Easy to add new validators
✅ **Type-Safe**: Uses Pydantic models for validation results
✅ **Comprehensive**: Provides detailed metrics and comparisons
✅ **Integrated**: Runs automatically with the main analysis
✅ **Logged**: All results saved to logs and Excel

## Usage

Simply run the main analysis:

```bash
uv run python -m muka_analysis.main
```

The validation will run automatically as Step 3 of the pipeline.

## Customization

You can adjust the tolerance for the group comparison validator by modifying the call in `validation.py`:

```python
result = validator_func(classified_farms, reference_df, tolerance_pct=10.0)  # 10% tolerance instead of 5%
```

Or add parameters to your custom validators as needed.
