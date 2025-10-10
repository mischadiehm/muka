# MuKa Farm Classification Analysis - Usage Guide

## Quick Start

### Installation with uv

```bash
cd /home/mischa/git/i/muka
uv sync  # Installs all dependencies automatically
```

### Running the Analysis - Modern CLI

The tool now features a modern CLI with Rich console output and Typer interface. Analysis results are beautifully displayed in the terminal, and Excel export is optional.

```bash
# Basic analysis - results shown in terminal, no Excel file
uv run python -m muka_analysis analyze

# Save analysis to Excel with default name (output/analysis_summary.xlsx)
uv run python -m muka_analysis analyze --save-analysis

# Specify custom input/output paths
uv run python -m muka_analysis analyze \
    --input csv/your_data.csv \
    --output output/results.csv

# Save analysis to custom Excel file
uv run python -m muka_analysis analyze \
    --excel custom_report.xlsx

# Force overwrite existing files
uv run python -m muka_analysis analyze \
    --force

# Enable verbose logging
uv run python -m muka_analysis analyze --verbose

# Show warnings for unclassified farms
uv run python -m muka_analysis analyze --show-unclassified-warnings

# Show detailed analysis of why farms were not classified
uv run python -m muka_analysis analyze --show-unclassified

# Combine options
uv run python -m muka_analysis analyze \
    --save-analysis \
    --verbose \
    --theme light \
    --force

# Get help for any command
uv run python -m muka_analysis --help
uv run python -m muka_analysis analyze --help
```

### Analysis Output

The analysis displays results directly in the terminal with:

- **Classification Results**: Overview of classified vs. unclassified farms
- **Group Distribution**: Table showing farms per group with percentages
- **Summary Statistics**: Key metrics (average/median animals, females) per group
- **Output Files**: Location of saved CSV and Excel files (if created)

Excel files are **only created when requested** using `--save-analysis` or `--excel` flags.

### Understanding Unclassified Farms

When farms cannot be classified, use the `--show-unclassified` flag to see detailed explanations:

```bash
uv run python -m muka_analysis analyze --show-unclassified
```

This provides:

- **Pattern Analysis**: Groups unclassified farms by their indicator patterns
- **Farm Characteristics**: Clear breakdown of what each farm has/doesn't have
- **Closest Matches**: Shows which classification profile is closest and why it doesn't match
- **Example Farms**: Sample farm IDs and their key metrics for each pattern
- **Summary Table**: Overview of all unclassified patterns with counts and percentages
- **Recommendations**: Suggestions for whether new profiles should be defined

**Example Output:**

```
📊 Pattern: [Dairy=0, Female=0, Arrivals=0, Leavings=1]
   Farms affected: 3,018

ℹ️  Farm characteristics:
   ✗ No female dairy cattle aged 3+
   ✗ No other female cattle aged 3+
   ✗ No calf arrivals under 85 days
   ✓ Has non-slaughter leavings under 51 days

⚠️  Why this pattern is not classified:
   Closest match would be 'Muku', but this farm:
     • has calf leavings (profile expects none)
```

This helps you understand whether unclassified farms represent:
- New valid farm types that need classification profiles
- Edge cases or transitional farm operations
- Potential data quality issues

### Validate CSV Files

Validate your data without running the full analysis:

```bash
# Validate input file
uv run python -m muka_analysis validate csv/your_data.csv

# Validate with verbose output
uv run python -m muka_analysis validate csv/your_data.csv --verbose
```

### Legacy Interface (for backward compatibility)

```bash
# Use the legacy main.py interface
uv run python -m muka_analysis.main \
    --input csv/your_data.csv \
    --output output/results.csv \
    --excel output/summary.xlsx
```

## Project Structure

```
muka/
├── pyproject.toml              # Project dependencies and configuration
├── README.md                   # Project overview
├── USAGE.md                    # This file - detailed usage guide
├── muka_analysis/              # Main package
│   ├── __init__.py            # Package initialization
│   ├── models.py              # Pydantic data models
│   ├── validators.py          # Data validation logic
│   ├── classifier.py          # Farm classification algorithm
│   ├── analyzer.py            # Statistical analysis
│   ├── io_utils.py            # File I/O utilities
│   └── main.py                # Main execution script
├── csv/                        # Input data directory
│   └── BetriebsFilter_Population_18_09_2025_guy_jr.csv
└── output/                     # Output results directory
    ├── classified_farms.csv   # Classified farm data
    └── analysis_summary.xlsx  # Statistical summary
```

## Farm Classification Groups

The tool classifies farms into 6 groups based on binary indicators:

### 1. **Muku** (Mother Cow Farms without Nurse Cows)
- No dairy cattle
- No other female cattle  
- No calf arrivals <85 days
- No non-slaughter leavings <51 days
- **Pattern**: [0, 0, 0, 0]

### 2. **Muku_Amme** (Mother Cow Farms with Nurse Cows)
- No dairy cattle
- No other female cattle
- Has calf arrivals <85 days
- No non-slaughter leavings <51 days
- **Pattern**: [0, 0, 1, 0]

### 3. **Milchvieh** (Dairy Farms)
- Has dairy cattle
- No other female cattle
- No calf arrivals <85 days
- Has non-slaughter leavings <51 days
- **Pattern**: [1, 0, 0, 1]

### 4. **BKMmZ** (Combined Keeping Dairy with Breeding)
- Has dairy cattle
- No other female cattle
- Has calf arrivals <85 days
- No non-slaughter leavings <51 days
- **Pattern**: [1, 0, 1, 0]

### 5. **BKMoZ** (Combined Keeping Dairy without Breeding)
- Has dairy cattle
- No other female cattle
- No calf arrivals <85 days
- No non-slaughter leavings <51 days
- **Pattern**: [1, 0, 0, 0]

### 6. **IKM** (Intensive Calf Rearing)
- No dairy cattle
- Has other female cattle
- Has calf arrivals <85 days
- No non-slaughter leavings <51 days
- **Pattern**: [0, 1, 1, 0]

## Input Data Format

The CSV file must contain the following columns:

### Required Columns
- `tvd`: Farm TVD identification number
- `farmTypeName`: Farm type name
- `Jahr`: Year of data collection
- `n_animals_total`: Total number of animals
- `n_females_age3_dairy`: Number of female dairy cattle aged 3+ years
- `n_days_female_age3_dairy`: Total days for female dairy cattle aged 3+ years
- `prop_days_female_age3_dairy`: Proportion of days for female dairy cattle
- `n_females_age3_total`: Total number of female cattle aged 3+ years
- `n_total_entries_younger85`: Total entries of animals younger than 85 days
- `n_total_leavings_younger51`: Total leavings of animals younger than 51 days
- `n_females_younger731`: Number of females younger than 731 days
- `prop_females_slaughterings_younger731`: Proportion of female slaughterings <731 days
- `n_animals_from51_to730`: Number of animals aged 51-730 days

### Binary Indicator Columns
- `1_femaleDairyCattle_V2`: Binary indicator (0/1) for female dairy cattle
- `2_femaleCattle`: Binary indicator (0/1) for other female cattle
- `3_calf85Arrivals`: Binary indicator (0/1) for calf arrivals <85 days
- `5_calf51nonSlaughterLeavings`: Binary indicator (0/1) for non-slaughter leavings <51 days

## Output Files

### 1. classified_farms.csv
Contains all input data plus the assigned `group` column for each farm.

### 2. analysis_summary.xlsx
Multi-sheet Excel workbook with:
- **Summary**: Key statistics by group (mean, median)
- **Detailed_Stats**: Full statistics (min, max, mean, median) for all metrics
- **Group_Counts**: Number of farms per group

## Usage Examples

### Example 1: Basic Analysis
```python
from pathlib import Path
from muka_analysis.main import main

# Run with default paths
main()
```

### Example 2: Custom Paths
```python
from pathlib import Path
from muka_analysis.main import main

main(
    input_file=Path("data/my_farms.csv"),
    output_file=Path("results/classified.csv"),
    excel_file=Path("results/summary.xlsx")
)
```

### Example 3: Using Components Individually
```python
from pathlib import Path
from muka_analysis.io_utils import IOUtils
from muka_analysis.classifier import FarmClassifier
from muka_analysis.analyzer import FarmAnalyzer

# Load data
farms = IOUtils.read_and_parse(Path("data/farms.csv"))

# Classify
classifier = FarmClassifier()
classified_farms = classifier.classify_farms(farms)

# Analyze
analyzer = FarmAnalyzer(classified_farms)
analyzer.print_summary()

# Get specific group
milchvieh_farms = analyzer.get_farms_by_group(FarmGroup.MILCHVIEH)
print(f"Found {len(milchvieh_farms)} dairy farms")
```

### Example 4: Get Summary Statistics
```python
from muka_analysis.analyzer import FarmAnalyzer

# After classification...
analyzer = FarmAnalyzer(classified_farms)

# Get counts per group
counts = analyzer.get_group_counts()
print(counts)

# Get summary statistics table
summary = analyzer.get_summary_by_group()
print(summary)

# Export to Excel
analyzer.export_summary_to_excel("my_analysis.xlsx")
```

## Validation and Error Handling

The tool includes comprehensive validation:

### Data Validation
- File existence and readability
- Required column presence
- Numeric type conversion
- Binary indicator validation (0 or 1 only)
- Proportion range validation (0 to 1)
- Missing value detection

### Classification Validation
- Farms that don't match any pattern are marked as "Unclassified"
- Warnings logged for unclassified farms with their binary patterns
- All validation warnings saved to `muka_analysis.log`

## Performance

On the test dataset (34,921 farms):
- **Load & Validate**: ~0.15 seconds
- **Classification**: ~0.2 seconds
- **Analysis**: ~0.15 seconds
- **Export**: ~0.3 seconds
- **Total**: ~0.8 seconds

## Extending the Tool

### Adding New Farm Groups

Edit `muka_analysis/classifier.py` and add to the `_create_profiles()` method:

```python
GroupProfile(
    group_name=FarmGroup.NEW_TYPE,
    female_dairy_cattle=0,  # 0 or 1
    female_cattle=1,        # 0 or 1
    calf_arrivals=0,        # 0 or 1
    calf_non_slaughter_leavings=1  # 0 or 1
),
```

### Adding New Metrics

1. Add field to `FarmData` model in `models.py`
2. Add to `NUMERIC_FIELDS` in `analyzer.py`
3. Update `dataframe_to_farm_data()` in `io_utils.py`
4. Update `REQUIRED_COLUMNS` in `validators.py`

## Troubleshooting

### Issue: "Missing required columns"
**Solution**: Check that your CSV has all required columns with exact names (case-sensitive)

### Issue: "Binary column contains invalid values"
**Solution**: Ensure binary indicator columns contain only 0 or 1

### Issue: "Failed to parse rows"
**Solution**: Check for:
- Non-numeric values in numeric columns
- Proportions outside [0, 1] range
- Missing data in required fields

### Issue: High number of unclassified farms
**Solution**: 
- Check the log file to see which binary patterns are unclassified
- Consider adding new farm group profiles for those patterns
- Verify binary indicators are calculated correctly in source data

## Logging

All operations are logged to `muka_analysis.log` in the current directory.

Log levels:
- **INFO**: Normal operations, counts, summaries
- **WARNING**: Non-critical issues (unclassified farms, validation warnings)
- **ERROR**: Critical failures

To adjust logging level, edit `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

## Testing

To run tests (when implemented):
```bash
uv pip install -e ".[dev]"
pytest
```

## Dependencies

Core:
- `pandas>=2.0.0` - Data manipulation
- `pydantic>=2.0.0` - Data validation
- `numpy>=1.24.0` - Numerical operations
- `openpyxl>=3.1.0` - Excel file writing

Development (optional):
- `pytest>=7.4.0` - Testing
- `black>=23.7.0` - Code formatting
- `mypy>=1.5.0` - Type checking
- `ruff>=0.0.285` - Linting

## License

Copyright © 2025 Research Team. All rights reserved.
