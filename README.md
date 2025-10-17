# MuKa Farm Classification and Analysis Tool

A Python package for classifying and analyzing farm data based on cattle types and movements.

## Features

- 🤖 **MCP Server** - Natural language data interaction via Model Context Protocol
- 🎨 **Modern CLI** with Rich console output and progress bars
- 🎭 **Theme Support** - Dark/Light mode switching for better accessibility
- ⚙️ **Centralized Configuration** - Type-safe settings via env vars, TOML, or defaults
- 🔧 **Type-safe** data validation with Pydantic v2
- 📊 **Comprehensive analysis** with Excel and CSV export
- 🚀 **Fast execution** with uv package management
- 📋 **Data validation** commands to check file quality
- 🎯 **Six farm group classifications** based on binary indicators
- 🔌 **Abstracted Output Interface** - Centralized logging and console management
- ⭐ **Multi-Mode Analysis** - Compare ALL 5 indicator modes in one command
- 📈 **Mode-Specific Naming** - Output files include indicator mode for traceability
- 🔬 **Advanced Filtering** - Percentile trimming and outlier detection (NEW!)
- 📉 **Outlier Analysis** - Statistical detection with IQR and z-score methods (NEW!)
- 📊 **Distribution Analysis** - Visualize data distributions with console histograms (NEW!)

## Quick Start

### Installation

```bash
git clone <repository>
cd muka
uv sync  # Installs all dependencies automatically
```

### Basic Usage

```bash
# Analyze with default settings - results shown in terminal
uv run python -m muka_analysis analyze

# Save detailed analysis to Excel file
uv run python -m muka_analysis analyze --save-analysis

# Analyze with specific indicator mode
uv run python -m muka_analysis analyze --mode 4-indicators --save-analysis

# ⭐ NEW: Analyze with ALL indicator modes (comprehensive comparison)
uv run python -m muka_analysis analyze-all-modes

# ⭐ NEW: All modes analysis with full data sheets
uv run python -m muka_analysis analyze-all-modes --include-data

# Specify custom files and theme
uv run python -m muka_analysis analyze \
    --input csv/your_data.csv \
    --output output/results.csv \
    --theme light

# Use light theme for better visibility
uv run python -m muka_analysis analyze --theme light

# Enable verbose logging
uv run python -m muka_analysis analyze --verbose

# Show warnings for farms that couldn't be classified
uv run python -m muka_analysis analyze --show-unclassified-warnings

# Save analysis to custom Excel file
uv run python -m muka_analysis analyze --excel custom_analysis.xlsx

# Validate data before analysis
uv run python -m muka_analysis validate csv/your_data.csv

# Get help
uv run python -m muka_analysis --help
```

### Theme Options

The CLI supports three color schemes:

- `--theme dark` (default): Optimized for dark terminals
- `--theme light`: Optimized for light terminals
- `--theme auto`: Auto-detect system theme (future feature)

All commands support theme switching to ensure comfortable viewing in any environment.

## ⭐ Multi-Mode Analysis (NEW!)

Analyze your farm data with **ALL 5 indicator modes** simultaneously and get a comprehensive comparison in a single Excel workbook!

### Quick Start

```bash
# Run all-modes analysis (summaries only - recommended)
uv run python -m muka_analysis analyze-all-modes

# Include full farm data for each mode (large file)
uv run python -m muka_analysis analyze-all-modes --include-data

# Custom output location
uv run python -m muka_analysis analyze-all-modes --output my_comparison.xlsx
```

### What You Get

The `analyze-all-modes` command generates a comprehensive Excel workbook with:

1. **Comparison_Summary** sheet - Cross-mode comparison showing:
   - Total farms analyzed
   - Classification success rates per mode
   - Group distribution counts and percentages
   - Side-by-side metrics across all modes

2. **Per-Mode Analysis** (for each of the 5 indicator modes):
   - `Data_{mode}` - Classified farm data (optional, with `--include-data`)
   - `Summary_{mode}` - Statistical summaries by farm group
   - `Counts_{mode}` - Farm counts per group

### The 5 Indicator Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **6-indicators** | All 6 fields, most strict | Research requiring strict classification |
| **6-indicators-flex** | All 6 fields, Milchvieh flexible on field 6 | Balanced approach with some flexibility |
| **4-indicators** | First 4 fields only (OLD method) | Maximum classification rate, most flexible |
| **5-indicators** | 5 fields, ignore female_slaughterings | Testing impact of field 5 |
| **5-indicators-flex** | 5 fields, Milchvieh flexible on field 6 | Middle ground between strict and flexible |

### Example Output

```
🐄 Classification Comparison Across Modes
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Mode              ┃ Classified ┃ Unclassified ┃ Success Rate ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 6-indicators      │ 9,132      │ 25,571       │ 26.3%        │
│ 6-indicators-flex │ 11,820     │ 22,883       │ 34.1%        │
│ 4-indicators      │ 25,828     │ 8,875        │ 74.4%        │
│ 5-indicators      │ 17,256     │ 17,447       │ 49.7%        │
│ 5-indicators-flex │ 20,794     │ 13,909       │ 59.9%        │
└───────────────────┴────────────┴──────────────┴──────────────┘

Key Insights:
📊 Highest classification rate: 4-indicators (74.4%)
🔒 Most strict classification: 6-indicators (26.3%)
```

### Mode-Specific Output Naming

When analyzing with a single mode using the `analyze` command, output files now automatically include the mode name:

```bash
# Single mode analysis
uv run python -m muka_analysis analyze --mode 4-indicators --save-analysis

# Generates:
#   output/classified_farms_4-indicators.csv
#   output/analysis_summary_4-indicators.xlsx
#     └─ Summary_4-indicators sheet
#     └─ Detailed_Stats_4-indicators sheet
#     └─ Group_Counts_4-indicators sheet
```

This ensures you can easily track which indicator mode was used and compare results across different runs.

### Configuration

Control output naming behavior in `muka_config.toml`:

```toml
[paths]
include_mode_in_filename = true   # Include mode name in output files (default: true)
all_modes_output_file = "all_modes_analysis.xlsx"  # Default output for all-modes
```

## 🔬 Advanced Filtering and Outlier Analysis (NEW!)

Perform sophisticated data filtering and outlier detection to focus your analysis on specific subsets of farms.

### What is Percentile Trimming and Why Use It?

**Percentile Explained:**
A percentile tells you the value below which a given percentage of data falls. For example:
- **10th percentile**: 10% of farms are below this value
- **90th percentile**: 90% of farms are below this value (10% are above)

**Why It Matters for Farm Data:**
Farm data often has extreme values - very small hobby farms and very large industrial operations. These extremes can:
- Skew your averages and statistics
- Hide patterns in "typical" farms
- Make comparisons difficult

**Trimming the top/bottom 10%** means:
- ✅ Remove the 10% smallest farms (e.g., incomplete data, hobby operations)
- ✅ Remove the 10% largest farms (e.g., industrial outliers)
- ✅ Keep the middle 80% - the "typical" farms showing meaningful patterns
- ✅ Get robust statistics not influenced by extremes

**Example:** With 1,000 farms:
- Before: Mean skewed by 100 extreme farms (50 tiny + 50 huge)
- After: Mean from 800 typical farms shows true pattern
- Result: Better understanding of what's normal

This is especially useful when analyzing metrics like `animalyear_days_female_age3_dairy` where the distribution has long tails.

### Quick Start

```bash
# Run the interactive demo with three examples
uv run python demo_filtering_outliers.py
```

### Example 1: Percentile Trimming

Remove extreme values to focus on "typical" farms:

```python
from muka_analysis.filters import DataFilter
from muka_analysis.analyzer import FarmAnalyzer

# Remove top/bottom 10% by animalyear_days_female_age3_dairy
filter_obj = DataFilter(farms)
filtered = filter_obj.trim_percentile(
    column="animalyear_days_female_age3_dairy",
    lower_percentile=0.10,  # Remove bottom 10%
    upper_percentile=0.90   # Remove top 10%
)

# Analyze filtered data
filtered_farms = filtered.get_filtered_farms()
analyzer = FarmAnalyzer(filtered_farms)
stats = analyzer.calculate_group_statistics()

# Show what was filtered
filtered.print_filter_summary(output)
```

### Example 2: Outlier Detection

Identify statistical outliers using IQR or z-score methods:

```python
from muka_analysis.analyzer import FarmAnalyzer

analyzer = FarmAnalyzer(farms)

# Detect outliers in multiple columns
outlier_report = analyzer.analyze_outliers(
    columns=[
        "animalyear_days_female_age3_dairy",
        "n_animals_total",
        "prop_days_female_age3_dairy",
    ],
    method="iqr",  # or "zscore"
    threshold=1.5  # IQR multiplier (1.5=standard, 3.0=extreme)
)

# Display results with statistics
analyzer.display_outlier_report(outlier_report, output)

# Show distribution summary
analyzer.display_distribution_summary(
    "animalyear_days_female_age3_dairy",
    by_group=True
)

# Create console histogram
analyzer.create_console_histogram(
    "animalyear_days_female_age3_dairy"
)
```

### Available Filters

- **Percentile Trimming**: `trim_percentile(column, lower, upper)`
- **Outlier Removal**: `remove_outliers(column, method, threshold)`
- **Value Range**: `filter_by_range(column, min_value, max_value)`
- **Group Filter**: `filter_by_group(FarmGroup.MUKU, ...)`
- **Custom Filter**: `filter_custom(lambda farm: condition, name)`

### Composable Filters

Chain multiple filters for sophisticated analysis:

```python
filtered = (
    DataFilter(farms)
    .exclude_unclassified()
    .trim_percentile("animalyear_days_female_age3_dairy", 0.10, 0.90)
    .remove_outliers("n_animals_total", method="iqr", threshold=1.5)
    .filter_by_range("year", min_value=2020)
)

# See all applied filters
filtered.print_filter_summary(output)
```

### Configuration

Customize filtering behavior in `muka_config.toml`:

```toml
[filtering]
default_outlier_method = "iqr"  # "iqr" or "zscore"
iqr_multiplier = 1.5            # 1.5=standard, 3.0=extreme
zscore_threshold = 3.0          # Standard: 3.0 (99.7% of data)
default_lower_percentile = 0.05 # 5%
default_upper_percentile = 0.95 # 95%
min_farms_after_filter = 10
warn_if_removed_pct = 0.20      # Warn if >20% removed

[visualization]
histogram_width = 60
histogram_bins = 20
show_percentiles = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
```

**See the complete guide**: `FILTERING_GUIDE.md`

## 🤖 MCP Server - Natural Language Interface

**NEW!** Interact with your farm data using natural language through our Model Context Protocol (MCP) server:

```bash
# Quick test with interactive client
uv run python interactive_mcp_client.py

# See ALL available commands and examples
# Type 'examples' in the interactive client for comprehensive guide

# Test with standalone script
uv run python test_mcp_server.py

# Use with Claude Desktop or any MCP client
# See MCP_QUICKSTART.md for setup
```

### Interactive Client Quick Start

The interactive MCP client provides a command-line interface to explore your farm data:

```bash
uv run python interactive_mcp_client.py
```

**Essential Commands:**

- `examples` - **Show comprehensive usage examples for ALL tools** ⭐
- `info` - Check data status
- `query group=Muku` - Filter farms by group
- `stats group=Milchvieh` - Get statistics for a group
- `question How many dairy farms?` - Ask in natural language
- `insights focus=outliers` - Find patterns
- `metric expression=n_animals_total.mean()` - Custom calculations
- `help` - Show command list
- `quit` - Exit

**Natural Language Examples:**

- "How many dairy farms have more than 100 animals?"
- "What's the average animal count for each group?"
- "Show me statistics for Muku farms"
- "Are there any outliers in the data?"
- "Compare dairy and Muku farms"
- "Export the analysis to Excel"

**Documentation:**

- **[MCP_QUICKSTART.md](MCP_QUICKSTART.md)** - 5-minute setup guide
- **[MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)** - Complete reference

## Configuration

The project uses a centralized configuration system with three priority levels:

1. **Environment Variables** (highest) - `MUKA_*` prefix
2. **Config File** - `muka_config.toml`
3. **Built-in Defaults** (lowest)

### Quick Configuration

```bash
# Set via environment variables
export MUKA_PATHS__CSV_DIR=/custom/data
export MUKA_PATHS__OUTPUT_DIR=/custom/output
export MUKA_OUTPUT__DEFAULT_THEME=light
export MUKA_ANALYSIS__MIN_GROUP_SIZE=10

# Or create muka_config.toml
cp muka_config.example.toml muka_config.toml
# Edit muka_config.toml with your settings
```

### Configuration Sections

- **`paths`** - File and directory paths
- **`classification`** - Classification thresholds and rules
- **`analysis`** - Statistical analysis settings
- **`validation`** - Data validation parameters
- **`output`** - Output formatting and display
- **`logging`** - Logging levels and formats

For complete documentation, see **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)**

## Project Structure

```text
muka_analysis/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── output.py            # Output interface abstraction
├── models.py            # Pydantic data models
├── validators.py        # Data validation logic
├── classifier.py        # Farm classification logic
├── analyzer.py          # Analysis and statistics
├── io_utils.py          # File I/O utilities
├── cli.py               # CLI interface
└── main.py              # Main execution script
```

## Farm Groups

- **Muku**: Mother cow farms without nurse cows
- **Muku_Amme**: Mother cow farms with nurse cows
- **Milchvieh**: Dairy farms
- **BKMmZ**: Combined keeping dairy with breeding
- **BKMoZ**: Combined keeping dairy without breeding
- **IKM**: Intensive calf rearing

## Documentation

- **[README.md](README.md)** - This file, project overview and quick start
- **[USAGE.md](USAGE.md)** - Detailed usage guide with examples
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Configuration system reference
- **[OUTPUT_INTERFACE_GUIDE.md](OUTPUT_INTERFACE_GUIDE.md)** - Developer guide for output interface
- **[VALIDATION.md](VALIDATION.md)** - Data validation documentation

See also:

- `demo_configuration.py` - Interactive configuration demo
- `demo_output_interface.py` - Output interface demo
- `muka_config.example.toml` - Example configuration file
