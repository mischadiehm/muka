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
