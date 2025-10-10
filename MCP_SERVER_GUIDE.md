# MuKa Analysis MCP Server

A Model Context Protocol (MCP) server that enables natural language interaction with MuKa farm classification and analysis data.

## 🚀 Overview

This MCP server provides a powerful interface to query, analyze, and gain insights from farm data through natural language. It exposes the complete MuKa analysis toolkit through MCP tools that can be used by any MCP-compatible client:

- **VS Code with GitHub Copilot** (Recommended)
- Claude Desktop
- Any MCP-compatible IDE or tool

## ✨ Features

### 🔧 Core Capabilities
- **Natural Language Queries**: Ask questions about farm data in plain language
- **Real-time Classification**: Classify farms into 6 groups based on cattle types and movements
- **Statistical Analysis**: Comprehensive statistics with min, max, mean, median for all metrics
- **Custom Calculations**: Perform custom aggregations and calculations on the data
- **Flexible Filtering**: Query farms by group, TVD, year, animal counts, and more
- **Excel Export**: Generate detailed multi-sheet analysis reports

### 📊 Available Tools

#### Data Management
1. **`load_farm_data`** - Load CSV data (uses default or custom file)
2. **`classify_farms`** - Classify loaded farms into groups
3. **`get_data_info`** - Check current data state and classification status

#### Querying
4. **`query_farms`** - Filter farms by group, TVD, year, animal counts
5. **`get_farm_details`** - Get complete details for a specific farm

#### Analysis
6. **`calculate_group_statistics`** - Comprehensive stats for groups
7. **`compare_groups`** - Side-by-side group comparisons
8. **`aggregate_by_field`** - Custom aggregations by any field
9. **`calculate_custom_metric`** - Advanced pandas-style calculations

#### Insights
10. **`get_data_insights`** - Generate automated insights (outliers, trends, distributions)
11. **`answer_question`** - Natural language Q&A about the data

#### Export
12. **`export_analysis`** - Export results to Excel with multiple sheets

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- uv package manager
- MCP-compatible client:
  - **VS Code** with GitHub Copilot extension (Recommended), OR
  - Claude Desktop, OR
  - Any other MCP-compatible tool

### Setup

1. **Install dependencies** (already done if you have the project):
   ```bash
   cd /home/mischa/git/i/muka
   uv sync
   ```

2. **Configure your MCP client**:

   **For VS Code + GitHub Copilot** (Recommended):
   
   Add to your VS Code settings JSON (`Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)"):
   ```json
   {
     "github.copilot.chat.mcp.servers": {
       "muka-analysis": {
         "command": "uv",
         "args": ["run", "python", "-m", "mcp_server"],
         "cwd": "/home/mischa/git/i/muka",
         "env": {
           "MUKA_DEBUG": "false"
         }
       }
     }
   }
   ```

   **For Claude Desktop**:
   
   Add to `~/.config/claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "muka-analysis": {
         "command": "uv",
         "args": ["run", "python", "-m", "mcp_server"],
         "cwd": "/home/mischa/git/i/muka",
         "env": {
           "MUKA_DEBUG": "false"
         }
       }
     }
   }
   ```

3. **Reload/Restart your client**:
   - VS Code: Command Palette → "Developer: Reload Window"
   - Claude Desktop: Completely restart the application

## 📖 Usage Examples

### Basic Workflow

**In VS Code Copilot Chat** (using `@muka-analysis`):

```
1. @muka-analysis load the default farm data
   → Uses load_farm_data tool

2. @muka-analysis classify all farms
   → Uses classify_farms tool

3. @muka-analysis how many farms are classified as dairy?
   → Uses answer_question tool

4. @muka-analysis show me statistics for Muku farms
   → Uses calculate_group_statistics tool

5. @muka-analysis compare dairy and Muku farms
   → Uses compare_groups tool

6. @muka-analysis export the analysis to Excel
   → Uses export_analysis tool
```

**In Claude Desktop** (direct natural language):

```
1. "Load the default farm data"
   → Uses load_farm_data tool

2. "Classify all farms"
   → Uses classify_farms tool

3. "How many farms are classified as dairy?"
   → Uses answer_question tool

4. "Show me statistics for Muku farms"
   → Uses calculate_group_statistics tool

5. "Compare dairy and Muku farms"
   → Uses compare_groups tool

6. "Export the analysis to Excel"
   → Uses export_analysis tool
```

### Natural Language Queries

**Counting & Percentages:**
- "How many farms do we have?"
- "What percentage of farms are Muku?"
- "Count dairy farms with more than 100 animals"

**Statistics & Averages:**
- "What's the average animal count by group?"
- "Which group has the highest average animals?"
- "Show me statistics for all groups"

**Filtering & Finding:**
- "Find all Muku farms from 2024"
- "Show me farms with more than 200 animals"
- "Get details for farm TVD 12345"

**Comparisons:**
- "Compare dairy and Muku farms"
- "How do all groups differ?"
- "Compare animal counts across groups"

**Insights & Patterns:**
- "Are there any outliers in the data?"
- "What are the main insights?"
- "Find unusual calf movement patterns"

**Custom Analysis:**
- "Calculate total animals by year"
- "Average dairy proportion per group"
- "Sum of calf arrivals by group and year"

## 🏗️ Architecture

### Server Structure
```
mcp_server/
├── __init__.py       # Package initialization
└── server.py         # Main MCP server implementation
```

### Key Components

1. **DataContext**: Manages data state throughout the session
   - Loads and caches data
   - Maintains classification state
   - Provides analyzer instance

2. **MCP Tools**: 12 tools for comprehensive data interaction
   - Automatically documented with descriptions
   - Input validation via JSON schema
   - Clear examples for natural language use

3. **Handler Functions**: Tool-specific logic
   - Error handling and validation
   - Result formatting
   - Integration with existing muka_analysis package

## 🔌 Integration with MuKa Analysis

The MCP server is a thin wrapper around the existing `muka_analysis` package:

- **Configuration**: Uses centralized `AppConfig` via `get_config()`
- **Models**: Leverages Pydantic v2 `FarmData` models
- **Classification**: Uses `FarmClassifier` for group assignment
- **Analysis**: Integrates `FarmAnalyzer` for statistics
- **Validation**: Employs existing validators

This ensures:
- ✅ Consistency with CLI tool
- ✅ Type safety via Pydantic
- ✅ Reusable business logic
- ✅ Minimal code duplication

## 🎯 Use Cases

### Research & Analysis
- Quick exploratory data analysis
- Statistical summaries for papers
- Outlier detection
- Group comparisons

### Data Quality
- Check classification distribution
- Validate data integrity
- Identify unusual patterns

### Reporting
- Generate Excel reports
- Extract specific metrics
- Create custom aggregations

### Interactive Exploration
- Ask ad-hoc questions
- Test hypotheses
- Deep-dive into specific farms

## 🔒 Configuration

The server respects all `muka_config.toml` settings:

- **Paths**: Input/output directories
- **Classification**: Thresholds and rules
- **Analysis**: Statistical parameters
- **Validation**: Data quality rules

Override via environment variables:
```bash
export MUKA_PATHS__CSV_DIR=/custom/data
export MUKA_ANALYSIS__MIN_GROUP_SIZE=50
```

## 🚦 Running the Server

### Via MCP Client (Recommended)
Just configure your MCP client and restart - it handles the server lifecycle.

### Standalone Testing
```bash
cd /home/mischa/git/i/muka
uv run python -m mcp_server.server
```

The server communicates via stdio (standard input/output), perfect for MCP protocol.

## 📝 Development

### Adding New Tools

1. **Define tool in `list_tools()`**:
   ```python
   Tool(
       name="my_new_tool",
       description="What it does and examples",
       inputSchema={...}
   )
   ```

2. **Add handler in `call_tool()`**:
   ```python
   elif name == "my_new_tool":
       result = await handle_my_new_tool(arguments)
   ```

3. **Implement handler function**:
   ```python
   async def handle_my_new_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
       # Your logic here
       return {"result": "..."}
   ```

### Best Practices
- ✅ Use type hints everywhere
- ✅ Validate inputs early
- ✅ Return structured Dict results
- ✅ Include helpful error messages
- ✅ Log important operations
- ✅ Follow existing patterns

## 🐛 Troubleshooting

### Server won't start
- Check uv is installed: `which uv`
- Verify Python path in config
- Check logs in MCP client

### Tools not working
- Ensure data is loaded first (`load_farm_data`)
- Classify before analysis (`classify_farms`)
- Check argument names match schema

### Data not found
- Verify CSV file path in config
- Check `MUKA_PATHS__CSV_DIR` env var
- Use absolute paths

### Type errors
- The server uses strict typing
- Check arguments match schema
- Review error messages carefully

## 🔮 Future Enhancements

Potential additions (not yet implemented):
- [ ] Streaming large result sets
- [ ] Caching for repeated queries
- [ ] Time-series analysis tools
- [ ] Visualization generation
- [ ] Multi-file analysis
- [ ] Export to more formats
- [ ] Advanced filtering DSL
- [ ] Saved query templates

## 📚 Related Documentation

- [Main README](../README.md) - Overview of MuKa Analysis
- [Configuration Guide](../CONFIGURATION_GUIDE.md) - Configuration system
- [Output Interface Guide](../OUTPUT_INTERFACE_GUIDE.md) - CLI and output
- [Usage Guide](../USAGE.md) - Command-line usage
- [Validation](../VALIDATION.md) - Data validation rules

## 🤝 Contributing

When contributing to the MCP server:
1. Follow project's Python conventions
2. Use type hints and Pydantic models
3. Add comprehensive docstrings
4. Test with actual MCP client
5. Document new tools clearly

## 📄 License

Same as the parent MuKa Analysis project.

## 💡 Tips

- **Start simple**: Load data, classify, ask basic questions
- **Build up**: Use simple queries to understand data before complex analysis
- **Combine tools**: Use insights from one query to inform the next
- **Export results**: Generate Excel reports for detailed offline analysis
- **Use natural language**: The `answer_question` tool understands many phrasings

## 🎉 Example Session

```
You: "Load the farm data"
Server: ✅ Loaded 1,234 farms from csv/BetriebsFilter_Population_18_09_2025_guy_jr.csv

You: "Classify all farms"
Server: ✅ Classified 1,234 farms into 6 groups:
  - Muku: 450
  - Milchvieh: 380
  - BKMmZ: 200
  - ...

You: "What percentage are dairy farms?"
Server: Dairy farms (Milchvieh) represent 30.8% of classified farms.

You: "Show me statistics for dairy farms"
Server: [Detailed statistics table...]

You: "Compare dairy and Muku farms on animal counts"
Server: [Comparison table showing mean/median differences...]

You: "Export this to Excel"
Server: ✅ Exported to output/analysis_summary.xlsx
```

## 🌟 Why MCP?

Model Context Protocol enables:
- **Universal interface**: Works with any MCP client
- **Natural interaction**: Ask questions, don't write code
- **State management**: Server maintains context
- **Type safety**: Structured tools with schemas
- **Composability**: Chain multiple tools together
- **Future-proof**: Compatible with emerging AI systems

---

**Made with ❤️ for research excellence, powered by MCP 🚀**
