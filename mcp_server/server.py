"""
MCP Server for MuKa Farm Data Analysis.

This server provides tools to query, analyze, and gain insights from farm data
through natural language interactions.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from mcp.server import Server
from mcp.types import TextContent, Tool

from muka_analysis.analyzer import FarmAnalyzer
from muka_analysis.classifier import FarmClassifier
from muka_analysis.config import get_config, init_config
from muka_analysis.io_utils import IOUtils
from muka_analysis.models import FarmData

logger = logging.getLogger(__name__)


def to_json_serializable(obj: Any) -> Any:
    """
    Convert numpy/pandas types to JSON-serializable Python types.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_json_serializable(item) for item in obj]
    elif hasattr(obj, "item"):  # Other numpy/pandas scalars
        return obj.item()
    else:
        return obj


class DataContext:
    """
    Context manager for farm data and analysis state.

    This class maintains the current state of loaded data, classifications,
    and analysis results throughout the MCP session.
    """

    def __init__(self, auto_load: bool = False) -> None:
        """
        Initialize data context.

        Args:
            auto_load: If True, automatically load and classify data on init
        """
        self.raw_df: Optional[pd.DataFrame] = None
        self.farms: Optional[List[FarmData]] = None
        self.analyzer: Optional[FarmAnalyzer] = None
        self.classifier: Optional[FarmClassifier] = None
        self.data_loaded: bool = False
        self.classified: bool = False

        if auto_load:
            self._auto_load_data()

    def load_data(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load farm data from CSV file.

        Args:
            file_path: Path to CSV file, or None to use default

        Returns:
            Dictionary with load status and info
        """
        config = get_config()

        if file_path is None:
            file_path = config.paths.get_default_input_path()

        try:
            self.raw_df = IOUtils.read_csv(file_path)
            self.data_loaded = True
            self.classified = False

            return {
                "success": True,
                "file": str(file_path),
                "rows": len(self.raw_df),
                "columns": len(self.raw_df.columns),
                "column_names": list(self.raw_df.columns),
            }
        except Exception as e:
            logger.error(f"Failed to load data: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def classify_farms(self) -> Dict[str, Any]:
        """
        Classify loaded farms into groups.

        Returns:
            Dictionary with classification results
        """
        if not self.data_loaded or self.raw_df is None:
            return {
                "success": False,
                "error": "No data loaded. Load data first.",
            }

        try:
            # Convert to FarmData objects
            self.farms = IOUtils.dataframe_to_farm_data(self.raw_df)

            # Classify farms
            self.classifier = FarmClassifier()
            self.farms = self.classifier.classify_farms(self.farms)

            # Initialize analyzer
            self.analyzer = FarmAnalyzer(self.farms)
            self.classified = True

            # Get classification summary
            group_counts = self.analyzer.get_group_counts()

            # Convert numpy types to Python types for JSON serialization
            group_counts = {k: int(v) for k, v in group_counts.items()}

            return {
                "success": True,
                "total_farms": len(self.farms),
                "classified_farms": sum(1 for f in self.farms if f.group is not None),
                "group_counts": group_counts,
            }
        except Exception as e:
            logger.error(f"Classification failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def _auto_load_data(self) -> None:
        """
        Automatically load all CSV files from the configured directory.

        This method is called during initialization if auto_load is True.
        It loads the first CSV file found in the csv directory and classifies farms.
        """
        try:
            config = get_config()
            csv_dir = config.paths.csv_dir

            # Find all CSV files in the directory
            csv_files = list(csv_dir.glob("*.csv"))

            if not csv_files:
                logger.warning(f"No CSV files found in {csv_dir}")
                return

            # Load the first CSV file (or combine all if multiple)
            if len(csv_files) == 1:
                logger.info(f"Auto-loading data from {csv_files[0]}")
                result = self.load_data(csv_files[0])
            else:
                # If multiple CSV files, load the first one
                # (you could enhance this to combine multiple files)
                logger.info(f"Found {len(csv_files)} CSV files, loading {csv_files[0]}")
                result = self.load_data(csv_files[0])

            if result.get("success"):
                logger.info(f"Successfully loaded {result.get('rows')} rows")

                # Automatically classify farms after loading
                classify_result = self.classify_farms()
                if classify_result.get("success"):
                    logger.info(
                        f"Successfully classified {classify_result.get('total_farms')} farms "
                        f"into {len(classify_result.get('group_counts', {}))} groups"
                    )
                else:
                    logger.error(f"Auto-classification failed: {classify_result.get('error')}")
            else:
                logger.error(f"Auto-load failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Auto-load data failed: {e}", exc_info=True)

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of current data state."""
        if not self.data_loaded:
            return {
                "loaded": False,
                "message": "No data loaded",
            }

        summary: Dict[str, Any] = {
            "loaded": True,
            "classified": self.classified,
            "total_rows": len(self.raw_df) if self.raw_df is not None else 0,
        }

        if self.classified and self.analyzer:
            # Convert numpy types to Python types for JSON serialization
            group_counts = self.analyzer.get_group_counts()
            summary["group_counts"] = {k: int(v) for k, v in group_counts.items()}

        return summary


# Initialize MCP server
server = Server("muka-analysis")

# Global data context - will be initialized with auto-load in main()
data_context = DataContext(auto_load=False)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """
    List all available tools for farm data analysis.

    This function defines the tools that can be called through the MCP server.
    Each tool is designed for natural language interaction with the data.
    """
    return [
        # Data Loading Tools
        Tool(
            name="load_farm_data",
            description=(
                "Load farm data from a CSV file. Use this as the first step before any analysis. "
                "If no file path is provided, loads the default configured file. "
                "Returns information about the loaded data including row count and column names."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to CSV file (optional, uses default if not provided)",
                    },
                },
            },
        ),
        Tool(
            name="classify_farms",
            description=(
                "Classify loaded farms into groups based on their characteristics. "
                "Must load data first using load_farm_data. "
                "Assigns each farm to one of six groups: Muku (mother cow), Muku_Amme (mother cow with nurse cows), "
                "Milchvieh (dairy), BKMmZ (combined dairy with breeding), BKMoZ (combined dairy without breeding), "
                "or IKM (intensive calf rearing). Returns classification summary with counts per group."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_data_info",
            description=(
                "Get information about currently loaded data and classification status. "
                "Shows whether data is loaded, whether it's classified, and basic counts. "
                "Use this to check the current state before running other operations."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Data Query Tools
        Tool(
            name="query_farms",
            description=(
                "Query farm data with flexible filters. Can filter by: "
                "- group: Farm group name (Muku, Milchvieh, BKMmZ, etc.) "
                "- tvd: Farm ID "
                "- year: Year of data "
                "- min_animals: Minimum total animals "
                "- max_animals: Maximum total animals "
                "Returns matching farms with all their data. "
                "Examples: 'Show me dairy farms with more than 100 animals', "
                "'Find all Muku farms from 2024', 'Get farms with TVD 12345'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "Filter by farm group (e.g., 'Muku', 'Milchvieh')",
                    },
                    "tvd": {
                        "type": "string",
                        "description": "Filter by specific farm TVD ID",
                    },
                    "year": {
                        "type": "integer",
                        "description": "Filter by year",
                    },
                    "min_animals": {
                        "type": "integer",
                        "description": "Minimum total animals",
                    },
                    "max_animals": {
                        "type": "integer",
                        "description": "Maximum total animals",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100)",
                        "default": 100,
                    },
                },
            },
        ),
        Tool(
            name="get_farm_details",
            description=(
                "Get detailed information about a specific farm by its TVD ID. "
                "Returns all data fields including classification indicators, animal counts, "
                "proportions, and group assignment. "
                "Example: 'Show me details for farm TVD 12345'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tvd": {
                        "type": "string",
                        "description": "Farm TVD ID to retrieve",
                    },
                },
                "required": ["tvd"],
            },
        ),
        # Statistical Analysis Tools
        Tool(
            name="calculate_group_statistics",
            description=(
                "Calculate comprehensive statistics for farm groups. "
                "Computes min, max, mean, and median for all numeric fields. "
                "Can calculate for all groups or a specific group. "
                "Returns statistics for fields like: animal counts, dairy cattle proportions, "
                "calf movements, and female cattle numbers. "
                "Examples: 'What are the statistics for dairy farms?', "
                "'Compare all groups statistically', 'Show me Muku farm statistics'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "Specific group to analyze (optional, analyzes all if not provided)",
                    },
                },
            },
        ),
        Tool(
            name="compare_groups",
            description=(
                "Compare key metrics between different farm groups. "
                "Shows side-by-side comparison of: total animals, dairy cattle, "
                "calf arrivals, calf leavings, and other important metrics. "
                "Useful for understanding differences between farm types. "
                "Example: 'Compare dairy farms to Muku farms', 'How do all groups differ?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of groups to compare (optional, compares all if not provided)",
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific metrics to compare (optional, uses key metrics if not provided)",
                    },
                },
            },
        ),
        # Advanced Calculation Tools
        Tool(
            name="calculate_custom_metric",
            description=(
                "Calculate a custom metric across farms using pandas-style expressions. "
                "Can perform calculations, aggregations, and filtering on the data. "
                "Supports mathematical operations, comparisons, and grouping. "
                "All column names are available as variables for direct access. "
                "\n\nSupported expression patterns:\n"
                "- Column operations: n_animals_total.sum(), n_animals_total.mean()\n"
                "- Comparisons: (n_animals_total > 100).sum()\n"
                "- Between: n_animals_total.between(50, 100).sum()\n"
                "- Multiple conditions: ((n_animals_total > 20) & (n_animals_total <= 50)).sum()\n"
                "- Methods: n_animals_total.gt(500).sum(), n_animals_total.lt(20).sum()\n"
                "- DataFrame access: df['column'].method() or df.column.method()\n"
                "\nExamples:\n"
                "'n_animals_total.sum()' - Sum all animals\n"
                "'n_animals_total.mean()' - Average animals per farm\n"
                "'(n_animals_total > 100).sum()' - Count farms with >100 animals\n"
                "'n_animals_total.between(50, 100).sum()' - Count farms with 50-100 animals\n"
                "'n_animals_total.describe()' - Full statistical summary"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Pandas-style calculation expression. "
                            "Column names can be used directly (e.g., n_animals_total.sum()). "
                            "Supports comparisons, boolean operations, and pandas methods."
                        ),
                    },
                    "group_by": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to group by (optional)",
                    },
                    "filter": {
                        "type": "string",
                        "description": "Filter expression (optional, pandas query syntax)",
                    },
                },
                "required": ["expression"],
            },
        ),
        Tool(
            name="aggregate_by_field",
            description=(
                "Aggregate data by a specific field with various statistics. "
                "Supports grouping by any field and calculating: sum, mean, median, min, max, count. "
                "Examples: "
                "'Sum total animals by year', "
                "'Average dairy cattle by group', "
                "'Count farms by group and year'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "group_by": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to group by",
                    },
                    "aggregate": {
                        "type": "object",
                        "description": "Dictionary of field: operation pairs (e.g., {'n_animals_total': 'sum'})",
                    },
                },
                "required": ["group_by", "aggregate"],
            },
        ),
        # Insight Generation Tools
        Tool(
            name="get_data_insights",
            description=(
                "Generate natural language insights about the data. "
                "Analyzes patterns, outliers, trends, and interesting findings. "
                "Can focus on specific aspects or provide general overview. "
                "Examples: "
                "'What are the main insights from this data?', "
                "'Tell me interesting patterns about dairy farms', "
                "'Find outliers in animal counts'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "description": "What to focus on (optional: 'outliers', 'trends', 'distribution', 'general')",
                    },
                    "group": {
                        "type": "string",
                        "description": "Specific group to analyze (optional)",
                    },
                },
            },
        ),
        Tool(
            name="answer_question",
            description=(
                "Answer a natural language question about the data. "
                "This is the most flexible tool - ask anything about the farm data, "
                "and it will use appropriate analysis methods to answer. "
                "Examples: "
                "'How many farms have more dairy cattle than other cattle?', "
                "'What percentage of farms are classified as Muku?', "
                "'Which group has the highest average animal count?', "
                "'Are there any farms with unusual calf movement patterns?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about the data",
                    },
                },
                "required": ["question"],
            },
        ),
        # Export Tools
        Tool(
            name="export_analysis",
            description=(
                "Export analysis results to Excel file with multiple sheets. "
                "Includes summary statistics, detailed stats, and group counts. "
                "Optionally includes validation comparison sheets. "
                "Example: 'Export the analysis to Excel'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path for output Excel file (optional, uses default if not provided)",
                    },
                    "include_validation": {
                        "type": "boolean",
                        "description": "Include validation comparison sheets (default: false)",
                        "default": False,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Handle tool calls from the MCP client.

    Args:
        name: Name of the tool to call
        arguments: Arguments passed to the tool

    Returns:
        List of TextContent with results
    """
    try:
        if name == "load_farm_data":
            result = await handle_load_data(arguments)
        elif name == "classify_farms":
            result = await handle_classify_farms(arguments)
        elif name == "get_data_info":
            result = await handle_get_data_info(arguments)
        elif name == "query_farms":
            result = await handle_query_farms(arguments)
        elif name == "get_farm_details":
            result = await handle_get_farm_details(arguments)
        elif name == "calculate_group_statistics":
            result = await handle_calculate_statistics(arguments)
        elif name == "compare_groups":
            result = await handle_compare_groups(arguments)
        elif name == "calculate_custom_metric":
            result = await handle_custom_metric(arguments)
        elif name == "aggregate_by_field":
            result = await handle_aggregate(arguments)
        elif name == "get_data_insights":
            result = await handle_get_insights(arguments)
        elif name == "answer_question":
            result = await handle_answer_question(arguments)
        elif name == "export_analysis":
            result = await handle_export(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.error(f"Tool call failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool Handler Functions
async def handle_load_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Load farm data from CSV file."""
    file_path = arguments.get("file_path")
    if file_path:
        file_path = Path(file_path)
    return data_context.load_data(file_path)


async def handle_classify_farms(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Classify farms into groups."""
    return data_context.classify_farms()


async def handle_get_data_info(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get current data state information."""
    return data_context.get_data_summary()


async def handle_query_farms(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Query farms with filters."""
    if not data_context.classified or data_context.farms is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    # Extract filters
    group = arguments.get("group")
    tvd = arguments.get("tvd")
    year = arguments.get("year")
    min_animals = arguments.get("min_animals")
    max_animals = arguments.get("max_animals")
    limit = arguments.get("limit", 100)

    # Filter farms
    filtered = data_context.farms

    if group:
        filtered = [
            f
            for f in filtered
            if f.group and (f.group.value if hasattr(f.group, "value") else f.group) == group
        ]

    if tvd:
        filtered = [f for f in filtered if f.tvd == tvd]

    if year:
        filtered = [f for f in filtered if f.year == year]

    if min_animals is not None:
        filtered = [f for f in filtered if f.n_animals_total >= min_animals]

    if max_animals is not None:
        filtered = [f for f in filtered if f.n_animals_total <= max_animals]

    # Limit results
    filtered = filtered[:limit]

    # Convert to dict format
    results = []
    for farm in filtered:
        group_value = None
        if farm.group:
            group_value = farm.group.value if hasattr(farm.group, "value") else farm.group

        results.append(
            {
                "tvd": farm.tvd,
                "year": farm.year,
                "group": group_value,
                "n_animals_total": farm.n_animals_total,
                "n_females_age3_dairy": farm.n_females_age3_dairy,
                "n_females_age3_total": farm.n_females_age3_total,
            }
        )

    result = {
        "count": len(results),
        "filters_applied": {k: v for k, v in arguments.items() if v is not None and k != "limit"},
        "farms": results,
    }
    return to_json_serializable(result)


async def handle_get_farm_details(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get detailed information for a specific farm."""
    if not data_context.classified or data_context.farms is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    tvd = arguments.get("tvd")

    # Find farm
    farm = next((f for f in data_context.farms if f.tvd == tvd), None)

    if not farm:
        return {"error": f"Farm with TVD {tvd} not found"}

    # Return all fields
    group_value = None
    if farm.group:
        group_value = farm.group.value if hasattr(farm.group, "value") else farm.group

    result = {
        "tvd": farm.tvd,
        "year": farm.year,
        "group": group_value,
        "classification_indicators": {
            "female_dairy_cattle_v2": farm.indicator_female_dairy_cattle_v2,
            "female_cattle": farm.indicator_female_cattle,
            "calf_arrivals": farm.indicator_calf_arrivals,
            "calf_leavings": farm.indicator_calf_leavings,
            "female_slaughterings": farm.indicator_female_slaughterings,
            "young_slaughterings": farm.indicator_young_slaughterings,
        },
        "animal_counts": {
            "n_animals_total": farm.n_animals_total,
            "n_females_age3_dairy": farm.n_females_age3_dairy,
            "n_females_age3_total": farm.n_females_age3_total,
            "n_females_younger731": farm.n_females_younger731,
            "n_animals_from51_to730": farm.n_animals_from51_to730,
        },
        "movements": {
            "n_total_entries_younger85": farm.n_total_entries_younger85,
            "n_total_leavings_younger51": farm.n_total_leavings_younger51,
        },
        "proportions": {
            "n_days_female_age3_dairy": farm.n_days_female_age3_dairy,
            "prop_days_female_age3_dairy": farm.prop_days_female_age3_dairy,
            "prop_females_slaughterings_younger731": farm.prop_females_slaughterings_younger731,
        },
    }
    return to_json_serializable(result)


async def handle_calculate_statistics(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate group statistics."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    group_name = arguments.get("group")

    # Convert group name to FarmGroup enum if provided
    from muka_analysis.models import FarmGroup

    group = None
    if group_name:
        try:
            # Try to match group name
            for g in FarmGroup:
                if g.value == group_name:
                    group = g
                    break
            if not group:
                return {"error": f"Unknown group: {group_name}"}
        except Exception as e:
            return {"error": f"Invalid group name: {e}"}

    stats_df = data_context.analyzer.calculate_group_statistics(group)

    return {
        "statistics": to_json_serializable(stats_df.to_dict(orient="records")),
    }


async def handle_compare_groups(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Compare metrics between groups."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    summary = data_context.analyzer.get_summary_by_group()

    groups_to_compare = arguments.get("groups")
    if groups_to_compare:
        summary = summary[summary["classification_pattern"].isin(groups_to_compare)]

    metrics = arguments.get("metrics")
    if metrics:
        # Keep classification_pattern and count, plus requested metrics
        cols_to_keep = ["classification_pattern", "count"] + [
            col for col in summary.columns if any(m in col for m in metrics)
        ]
        summary = summary[[col for col in cols_to_keep if col in summary.columns]]

    return {
        "comparison": to_json_serializable(summary.to_dict(orient="records")),
    }


async def handle_custom_metric(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate custom metric using pandas expressions."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    expression = arguments.get("expression")
    if not expression:
        return {"error": "Expression is required"}

    group_by = arguments.get("group_by")
    filter_expr = arguments.get("filter")

    df = data_context.analyzer.df.copy()

    # Apply filter if provided
    if filter_expr:
        try:
            df = df.query(filter_expr)
        except Exception as e:
            return {"error": f"Filter expression failed: {e}"}

    # Apply grouping if provided
    if group_by:
        try:
            # Evaluate expression on grouped data
            result = df.groupby(group_by).agg(eval(f"lambda x: {expression}"))
            return {"result": to_json_serializable(result.to_dict())}
        except Exception as e:
            return {"error": f"Calculation failed: {e}"}
    else:
        try:
            # Create a safe evaluation context with access to df, pd, and individual columns
            # This allows expressions like: n_animals_total.sum(), (n_animals_total > 100).sum(), etc.
            eval_context = {
                "df": df,
                "pd": pd,
                "__builtins__": {},  # Restrict built-ins for safety
            }

            # Add all column names as variables pointing to the Series
            for col in df.columns:
                eval_context[col] = df[col]

            # Evaluate the expression with the enriched context
            # This supports both df.column.method() and column.method() syntax
            if expression.startswith("df.") or expression.startswith("df["):
                # Expression already references df explicitly
                result = eval(expression, eval_context)
            else:
                # Expression uses column names directly or pandas methods
                result = eval(expression, eval_context)

            # Handle different result types and ensure JSON serializability
            if isinstance(result, pd.Series):
                return {"result": to_json_serializable(result.to_dict())}
            elif isinstance(result, pd.DataFrame):
                return {"result": to_json_serializable(result.to_dict(orient="records"))}
            else:
                # Convert numpy/pandas types to native Python types for JSON serialization
                return {"result": to_json_serializable(result)}
        except Exception as e:
            logger.error(f"Custom metric calculation failed: {expression}", exc_info=True)
            return {"error": f"Calculation failed: {e}"}


async def handle_aggregate(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate data by fields."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    group_by = arguments.get("group_by", [])
    aggregate = arguments.get("aggregate", {})

    if not group_by or not aggregate:
        return {"error": "Both group_by and aggregate are required"}

    df = data_context.analyzer.df

    try:
        result = df.groupby(group_by).agg(aggregate).reset_index()
        return {
            "result": to_json_serializable(result.to_dict(orient="records")),
        }
    except Exception as e:
        return {"error": f"Aggregation failed: {e}"}


async def handle_get_insights(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate data insights."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    focus = arguments.get("focus", "general")
    group = arguments.get("group")

    insights = []

    df = data_context.analyzer.df
    if group:
        df = df[df["group"] == group]

    # General insights
    insights.append(f"Total farms: {len(df)}")

    # Group distribution
    group_counts = data_context.analyzer.get_group_counts()
    insights.append(f"Group distribution: {group_counts}")

    # Statistical insights
    if focus in ["general", "distribution"]:
        avg_animals = df["n_animals_total"].mean()
        median_animals = df["n_animals_total"].median()
        insights.append(f"Average animals per farm: {avg_animals:.1f}")
        insights.append(f"Median animals per farm: {median_animals:.1f}")

    # Outlier detection
    if focus in ["general", "outliers"]:
        Q1 = df["n_animals_total"].quantile(0.25)
        Q3 = df["n_animals_total"].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df["n_animals_total"] < Q1 - 1.5 * IQR) | (df["n_animals_total"] > Q3 + 1.5 * IQR)
        ]
        if len(outliers) > 0:
            insights.append(f"Found {len(outliers)} outlier farms based on animal count")

    return {
        "insights": insights,
        "focus": focus,
    }


async def handle_answer_question(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Answer natural language question about the data."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    question = arguments.get("question", "").lower()

    df = data_context.analyzer.df

    answer_parts = []

    # Try to understand and answer the question
    if "how many" in question or "count" in question:
        if "dairy" in question:
            count = len(df[df["group"] == "Milchvieh"])
            answer_parts.append(f"There are {count} dairy farms (Milchvieh).")
        elif "muku" in question:
            count = len(df[df["group"].str.contains("Muku", na=False)])
            answer_parts.append(f"There are {count} Muku farms.")
        else:
            answer_parts.append(f"Total farms: {len(df)}")

    if "percentage" in question or "percent" in question:
        if "muku" in question:
            total = len(df[df["group"].notna()])
            muku_count = len(df[df["group"].str.contains("Muku", na=False)])
            pct = (muku_count / total * 100) if total > 0 else 0
            answer_parts.append(f"Muku farms represent {pct:.1f}% of classified farms.")

    if "average" in question or "mean" in question:
        if "animal" in question:
            avg = df["n_animals_total"].mean()
            answer_parts.append(f"Average animals per farm: {avg:.1f}")

            # Break down by group if asking about comparison
            if "group" in question:
                group_avgs = df.groupby("group")["n_animals_total"].mean()
                answer_parts.append("Average by group:")
                for group, avg in group_avgs.items():
                    answer_parts.append(f"  {group}: {avg:.1f}")

    if "highest" in question or "most" in question:
        if "animal" in question and "group" in question:
            group_avgs = df.groupby("group")["n_animals_total"].mean().sort_values(ascending=False)
            highest = group_avgs.index[0]
            highest_avg = group_avgs.iloc[0]
            answer_parts.append(
                f"The group with highest average animals is {highest} with {highest_avg:.1f} animals."
            )

    if "unusual" in question or "outlier" in question:
        Q1 = df["n_animals_total"].quantile(0.25)
        Q3 = df["n_animals_total"].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df["n_animals_total"] < Q1 - 1.5 * IQR) | (df["n_animals_total"] > Q3 + 1.5 * IQR)
        ]
        answer_parts.append(f"Found {len(outliers)} farms with unusual values.")
        if len(outliers) > 0:
            answer_parts.append(
                f"Animal count range for outliers: {outliers['n_animals_total'].min():.0f} to {outliers['n_animals_total'].max():.0f}"
            )

    if not answer_parts:
        answer_parts.append(
            "I couldn't determine a specific answer. Try asking about: counts, percentages, averages, groups, or outliers."
        )

    return {
        "question": question,
        "answer": " ".join(answer_parts),
    }


async def handle_export(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Export analysis to Excel file."""
    if not data_context.classified or data_context.analyzer is None:
        return {"error": "Data not loaded or classified. Load and classify data first."}

    config = get_config()
    file_path = arguments.get("file_path")
    if not file_path:
        file_path = config.paths.output_dir / "analysis_summary.xlsx"
    else:
        file_path = Path(file_path)

    include_validation = arguments.get("include_validation", False)

    try:
        data_context.analyzer.export_summary_to_excel(
            str(file_path), include_validation=include_validation
        )
        return {
            "success": True,
            "file": str(file_path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def main() -> None:
    """Run the MCP server."""
    # Initialize configuration first
    init_config()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting MuKa Analysis MCP Server...")

    # Auto-load data from CSV directory
    logger.info("Auto-loading farm data from CSV directory...")
    data_context._auto_load_data()

    if data_context.data_loaded:
        logger.info("✓ Data loaded and classified, ready for queries!")
    else:
        logger.warning("⚠ No data loaded - server starting without data")

    # Run the server
    import asyncio

    from mcp.server.stdio import stdio_server

    async def run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
