# MuKa Farm Classification and Analysis Tool

A Python package for classifying and analyzing farm data based on cattle types and movements.

## Features

- 🎨 **Modern CLI** with Rich console output and progress bars
- 🎭 **Theme Support** - Dark/Light mode switching for better accessibility
- 🔧 **Type-safe** data validation with Pydantic v2
- 📊 **Comprehensive analysis** with Excel and CSV export
- 🚀 **Fast execution** with uv package management
- 📋 **Data validation** commands to check file quality
- 🎯 **Six farm group classifications** based on binary indicators
- 🔌 **Abstracted Output Interface** - Centralized logging and console management

## Quick Start

### Installation

```bash
git clone <repository>
cd muka
uv sync  # Installs all dependencies automatically
```

### Basic Usage

```bash
# Analyze with default settings (dark theme)
uv run python -m muka_analysis analyze

# Specify custom files and theme
uv run python -m muka_analysis analyze \
    --input csv/your_data.csv \
    --output output/results.csv \
    --excel output/summary.xlsx \
    --theme light

# Use light theme for better visibility
uv run python -m muka_analysis analyze --theme light

# Enable verbose logging
uv run python -m muka_analysis analyze --verbose

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

## Project Structure

```
muka_analysis/
├── __init__.py          # Package initialization
├── models.py            # Pydantic data models
├── validators.py        # Data validation logic
├── classifier.py        # Farm classification logic
├── analyzer.py          # Analysis and statistics
├── io_utils.py          # File I/O utilities
└── main.py             # Main execution script
```

## Farm Groups

- **Muku**: Mother cow farms without nurse cows
- **Muku_Amme**: Mother cow farms with nurse cows
- **Milchvieh**: Dairy farms
- **BKMmZ**: Combined keeping dairy with breeding
- **BKMoZ**: Combined keeping dairy without breeding
- **IKM**: Intensive calf rearing
