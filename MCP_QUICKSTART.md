# Quick Start: MuKa Analysis MCP Server for VS Code

Get up and running with the MCP server in VS Code with GitHub Copilot in 5 minutes!

## What is this?

An MCP server that lets you interact with farm data using **natural language** through GitHub Copilot in VS Code. Ask questions like:

- "How many dairy farms do we have?"
- "What's the average animal count for Muku farms?"
- "Show me farms with more than 200 animals"
- "Are there any outliers in the data?"

## Prerequisites

- **VS Code** (Visual Studio Code) installed
- **GitHub Copilot** extension installed and active
- **Python 3.10+** and **uv** package manager
- This repository cloned locally

## Setup for VS Code + GitHub Copilot

### 1. Open VS Code Settings for MCP

Open your VS Code settings JSON file:

**Option A - Via Command Palette:**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type: "Preferences: Open User Settings (JSON)"
3. Press Enter

**Option B - Via Settings UI:**
1. Go to File → Preferences → Settings (or Code → Settings on macOS)
2. Click the "Open Settings (JSON)" icon in the top-right corner

### 2. Add MCP Server Configuration

Add the following to your `settings.json`:

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

**Important:** Change the `cwd` path to your actual repository location!

**Examples:**
- Linux: `"/home/yourusername/projects/muka"`
- macOS: `"/Users/yourusername/projects/muka"`
- Windows: `"C:\\Users\\yourusername\\projects\\muka"`

### 3. Reload VS Code

After saving the settings:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type: "Developer: Reload Window"
3. Press Enter

Or simply restart VS Code completely.

### 4. Verify MCP Server is Available

1. Open GitHub Copilot Chat in VS Code:
   - Click the chat icon in the left sidebar, OR
   - Press `Ctrl+Alt+I` (or `Cmd+Opt+I` on macOS), OR
   - Use Command Palette: "GitHub Copilot: Open Chat"

2. In the chat, type `@` and you should see "muka-analysis" in the suggestions

3. If you see it, you're ready to go! 🎉

## Quick Test (Without MCP Client)

Test the server locally:

```bash
cd /home/mischa/git/i/muka
uv run python test_mcp_server.py
```

You should see:
```
🎉🎉🎉 All MCP server tests passed successfully! 🎉🎉🎉
```

## Usage Examples in VS Code Copilot Chat

Once set up, open Copilot Chat and reference the MCP server with `@muka-analysis`:

**Example Conversation:**

```
You: @muka-analysis load the farm data

Copilot: ✅ Loaded 34,923 farms from csv/BetriebsFilter_Population_18_09_2025_guy_jr.csv

You: @muka-analysis classify all the farms

Copilot: ✅ Classified 25,940 farms into 6 groups:
- Milchvieh: 12,006
- Muku: 6,069
- BKMoZ: 3,776
...

You: @muka-analysis what percentage are dairy farms?

Copilot: Dairy farms (Milchvieh) represent 46.3% of classified farms.

You: @muka-analysis show me statistics for Muku farms

Copilot: [Statistics table with averages, min, max, median...]

You: @muka-analysis which group has the highest average animals?

Copilot: IKM (Intensive calf rearing) has the highest average with 220.1 animals per farm.

You: @muka-analysis compare dairy and Muku farms

Copilot: [Detailed comparison table...]

You: @muka-analysis export the analysis to Excel

Copilot: ✅ Exported to output/analysis_summary.xlsx
```

**Pro Tips:**
- Use `@muka-analysis` at the start of your message to invoke the server
- Be conversational - Copilot understands natural language
- Chain questions together for deeper analysis
- Ask follow-up questions to drill down into the data

## Available Tools

The server provides 12 tools:

1. **load_farm_data** - Load CSV data
2. **classify_farms** - Classify into groups
3. **get_data_info** - Check current state
4. **query_farms** - Filter and find farms
5. **get_farm_details** - Get specific farm info
6. **calculate_group_statistics** - Statistical analysis
7. **compare_groups** - Compare different groups
8. **aggregate_by_field** - Custom aggregations
9. **calculate_custom_metric** - Advanced calculations
10. **get_data_insights** - Auto-generated insights
11. **answer_question** - Natural language Q&A
12. **export_analysis** - Export to Excel

## Advanced Configuration

The server uses your `muka_config.toml` settings. You can override with environment variables in your VS Code settings:

```json
{
  "github.copilot.chat.mcp.servers": {
    "muka-analysis": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server"],
      "cwd": "/path/to/your/muka",
      "env": {
        "MUKA_PATHS__CSV_DIR": "/custom/data/path",
        "MUKA_PATHS__OUTPUT_DIR": "/custom/output",
        "MUKA_OUTPUT__DEFAULT_THEME": "dark",
        "MUKA_DEBUG": "true"
      }
    }
  }
}
```

**Common Environment Variables:**
- `MUKA_PATHS__CSV_DIR` - Custom data directory
- `MUKA_PATHS__OUTPUT_DIR` - Custom output directory
- `MUKA_DEBUG` - Enable debug logging
- `MUKA_OUTPUT__DEFAULT_THEME` - Theme (dark/light)

## Troubleshooting

### MCP Server not showing up in Copilot Chat

**Solution 1 - Check Settings:**
1. Open VS Code settings JSON (`Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)")
2. Verify the `github.copilot.chat.mcp.servers` section exists
3. Check JSON syntax is valid (no missing commas, brackets, etc.)
4. Verify `cwd` path is correct and uses the right slash style for your OS

**Solution 2 - Reload Window:**
1. Save your settings.json
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
3. Type "Developer: Reload Window"
4. Wait for VS Code to fully reload

**Solution 3 - Check GitHub Copilot:**
1. Ensure GitHub Copilot extension is installed and active
2. Check you're signed in to GitHub in VS Code
3. Verify Copilot Chat is working (open chat panel)

**Solution 4 - Check Logs:**
1. Open Output panel: View → Output
2. Select "GitHub Copilot Chat" from the dropdown
3. Look for MCP server connection errors

### @muka-analysis not appearing in suggestions

1. Type `@` in Copilot Chat - wait a moment for suggestions
2. If not showing, reload window (see Solution 2 above)
3. Check the Output logs for errors
4. Verify the server name exactly matches: `"muka-analysis"`

### Tools not working properly

**Always follow this order:**
1. First: `@muka-analysis load the farm data`
2. Then: `@muka-analysis classify all farms`
3. Now you can query and analyze

**Example error:**
```
You: @muka-analysis show me statistics
Error: Data not loaded or classified
```

**Fix:**
```
You: @muka-analysis load the farm data
You: @muka-analysis classify all the farms
You: @muka-analysis show me statistics  ✅ Now it works!
```

### Python/UV/Path errors

**Test the server manually:**
```bash
# Navigate to your repository
cd /path/to/your/muka

# Test the server works
uv run python test_mcp_server.py

# Should show: 🎉🎉🎉 All tests passed! 🎉🎉🎉
```

**If test fails:**
```bash
# Verify uv is installed
which uv

# Re-sync dependencies
uv sync

# Try test again
uv run python test_mcp_server.py
```

### Common Path Issues

**Wrong:**
```json
"cwd": "~/projects/muka"  ❌ Don't use ~
"cwd": "$HOME/projects/muka"  ❌ Don't use variables
```

**Correct:**
```json
"cwd": "/home/username/projects/muka"  ✅ Linux/Mac
"cwd": "C:\\Users\\username\\projects\\muka"  ✅ Windows
```

### Still not working?

1. Check VS Code version (needs recent version for MCP support)
2. Update GitHub Copilot extension
3. Look for error messages in:
   - VS Code Output panel (View → Output)
   - Terminal where you run the test script
4. Make sure Python 3.10+ is available: `python3 --version`

## Next Steps

- Read full documentation: [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)
- Explore example queries
- Customize for your data
- Integrate with other MCP clients

## VS Code-Specific Tips

### Keyboard Shortcuts

- **Open Copilot Chat**: `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Opt+I` (macOS)
- **Command Palette**: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
- **Toggle Terminal**: `` Ctrl+` `` (all platforms)

### Workflow Tips

1. **Keep Chat Open**: Pin the Copilot Chat panel to the side for easy access
2. **Use Terminal**: Run `uv run python example_mcp_usage.py` in VS Code terminal
3. **Multi-turn Conversations**: Build on previous questions for deeper analysis
4. **Copy Results**: Use the copy button to grab analysis results

### Testing in VS Code

```bash
# Open integrated terminal (Ctrl+`)
cd /path/to/your/muka

# Run comprehensive tests
uv run python test_mcp_server.py

# See example workflows
uv run python example_mcp_usage.py
```

## Quick Reference Card

| Action | Command |
|--------|---------|
| Open Chat | `Ctrl+Alt+I` or click chat icon |
| Reference Server | `@muka-analysis your question` |
| Load Data | `@muka-analysis load farm data` |
| Classify | `@muka-analysis classify all farms` |
| Query | `@muka-analysis show farms with >100 animals` |
| Statistics | `@muka-analysis statistics for Muku farms` |
| Compare | `@muka-analysis compare dairy and Muku` |
| Export | `@muka-analysis export to Excel` |

## Need More Help?

If you get stuck:

1. **Test locally**: `uv run python test_mcp_server.py`
2. **Check VS Code Output**: View → Output → "GitHub Copilot Chat"
3. **Verify paths**: Make sure `cwd` in settings.json is correct
4. **Reload window**: Command Palette → "Developer: Reload Window"
5. **Check dependencies**: `uv sync` in your terminal

## Next Steps

- 📚 Read full documentation: [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)
- 💻 Try example workflows: `uv run python example_mcp_usage.py`
- 🎯 Explore all 12 tools in the guide
- 🔧 Customize configuration in `muka_config.toml`

---

**Happy analyzing with VS Code + Copilot! 🎉✨**
