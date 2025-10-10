# MCP Server Auto-Load Feature

## Summary

The MCP server now **automatically loads and classifies farm data** on startup. You no longer need to manually call the `load_farm_data` tool - data is ready immediately when the server starts!

## How It Works

### Server Startup Sequence

1. **Initialize Configuration** - Loads settings from `muka_config.toml` and environment variables
2. **Setup Logging** - Configures logging with INFO level
3. **Auto-Load Data** - Automatically:
   - Scans the configured CSV directory (`csv/` by default)
   - Loads the first CSV file found
   - Validates and parses farm data
   - Classifies farms into groups (Muku, Milchvieh, BKMmZ, etc.)
4. **Start MCP Server** - Begins accepting tool calls with data already loaded

### Configuration

The auto-load feature uses your configuration settings:

```toml
[paths]
csv_dir = "csv"  # Directory to scan for CSV files
default_input = "BetriebsFilter_Population_18_09_2025_guy_jr.csv"
```

Or via environment variables:

```bash
export MUKA_PATHS__CSV_DIR=/path/to/csv/files
```

## What Changed

### Before (Manual Load)

```python
# Old workflow - had to manually load
1. Start server
2. Call load_farm_data tool
3. Call classify_farms tool
4. Now can query data
```

### After (Auto-Load)

```python
# New workflow - data ready immediately
1. Start server ← data is automatically loaded and classified!
2. Query data immediately with any tool
```

## Interactive Client

The interactive client also benefits from auto-load:

```bash
$ ./test-mcp

🐄 MuKa Farm Data Analysis - Interactive MCP Client
✓ Configuration loaded
✓ Auto-loaded 34923 farms (7 groups)

muka> question How many dairy farms are there?
# Works immediately - no need to load/classify first!
```

## MCP Tools Status

The `load_farm_data` and `classify_farms` tools are **still available** if you need to:
- Reload data from a different file
- Re-classify farms with different parameters
- Refresh data that has changed

But for normal usage, you can skip straight to querying and analyzing!

## Benefits

✅ **Faster workflow** - No manual initialization steps
✅ **Better UX** - Data ready when you need it
✅ **Fewer errors** - No "data not loaded" messages
✅ **Simpler scripts** - Skip the initialization boilerplate

## Server Logs

When the server starts, you'll see:

```
2025-10-10 12:19:25 - Starting MuKa Analysis MCP Server...
2025-10-10 12:19:25 - Auto-loading farm data from CSV directory...
2025-10-10 12:19:25 - Auto-loading data from csv/BetriebsFilter_Population_18_09_2025_guy_jr.csv
2025-10-10 12:19:27 - Successfully loaded 34923 rows
2025-10-10 12:19:27 - Successfully classified 34921 farms into 7 groups
2025-10-10 12:19:27 - ✓ Data loaded and classified, ready for queries!
```

## Edge Cases

### No CSV Files Found

If no CSV files exist in the directory:
```
⚠ No CSV files found in csv/
⚠ No data loaded - server starting without data
```

The server still starts, but you'll need to manually load data.

### Multiple CSV Files

If multiple CSV files are found:
```
Found 3 CSV files, loading BetriebsFilter_Population_18_09_2025_guy_jr.csv
```

The server loads the first file alphabetically. To load a different file, use the `load_farm_data` tool.

### Load Errors

If auto-load fails (corrupt file, wrong format, etc.):
```
⚠ Auto-load failed: Error message here
⚠ No data loaded - server starting without data
```

The server continues to run, and you can manually load valid data.

## Implementation Details

### Code Changes

1. **DataContext.__init__()** - Added `auto_load` parameter
2. **DataContext._auto_load_data()** - New method that:
   - Finds CSV files in configured directory
   - Loads the first file
   - Automatically classifies farms
   - Logs results
3. **main()** - Calls `_auto_load_data()` after config initialization

### Backward Compatibility

✅ **Fully backward compatible** - All existing tools work exactly as before
✅ **Optional feature** - Can disable by not having CSV files in the directory
✅ **Manual override** - Can still manually load different files

## Testing

Test the auto-load feature:

```bash
# Interactive client
./test-mcp
# Should show: "✓ Auto-loaded X farms (Y groups)"

# Or programmatically
uv run python -c "
from muka_analysis.config import init_config
from mcp_server.server import DataContext

init_config()
ctx = DataContext(auto_load=True)
print(f'Loaded: {ctx.data_loaded}, Classified: {ctx.classified}')
print(f'Farms: {len(ctx.farms) if ctx.farms else 0}')
"
```

## Questions?

- **How do I disable auto-load?** - Remove CSV files from the directory, or the server will start without data
- **How do I load a different file?** - Use the `load_farm_data` tool with a specific file path
- **Does this work with multiple workspaces?** - Yes, each workspace's CSV directory is scanned independently
- **What if data changes?** - Call `load_farm_data` to reload, or restart the server

---

**Auto-load makes the MCP server truly plug-and-play!** 🚀
