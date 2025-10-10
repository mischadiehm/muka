# Enhanced CLI Experience with Tab Completion

The interactive MCP client now features a **rich command-line experience** with:
- ✅ **Tab completion** for commands and parameters
- ✅ **Command history** (navigate with up/down arrows)
- ✅ **In-line editing** (Emacs-style shortcuts)
- ✅ **Smart parameter completion** for groups, filters, etc.
- ✅ **Persistent history** across sessions

## Quick Setup

Install the enhanced CLI features:

```bash
./setup-mcp-client
```

Or manually:

```bash
uv add prompt_toolkit
```

Then run the client:

```bash
./test-mcp
```

## Tab Completion Features

### Command Completion

Type the first few letters of a command and press **Tab**:

```bash
muka> qu<Tab>
# Completes to: query

muka> cla<Tab>
# Completes to: classify
```

### Available Commands (Tab-complete)

- `info` - Show data status
- `load` - Reload data
- `classify` - Re-classify farms
- `query` - Query farms with filters
- `stats` - Calculate statistics
- `question` - Ask natural language questions
- `insights` - Get data insights
- `farm` - Get farm details
- `compare` - Compare groups
- `aggregate` - Aggregate data
- `metric` - Calculate custom metrics
- `export` - Export to Excel
- `help` - Show help
- `clear` - Clear screen
- `quit` / `exit` - Exit client

### Parameter Completion

Tab completion works for parameters too:

```bash
muka> query <Tab>
# Shows: group=  tvd=  year=  min_animals=  max_animals=

muka> query g<Tab>
# Completes to: query group=

muka> query group=<Tab>
# Shows: Muku  Muku_Amme  Milchvieh  BKMmZ  BKMoZ  IKM

muka> query group=Mu<Tab>
# Shows: Muku  Muku_Amme

muka> stats <Tab>
# Shows: group=

muka> insights <Tab>
# Shows: focus=outliers  focus=trends  focus=distribution  focus=general  group=
```

### Smart Context-Aware Completion

The completer understands context:

```bash
# For query command
muka> query group=Muku min<Tab>
# Completes to: query group=Muku min_animals=

# For stats command
muka> stats group=<Tab>
# Shows all group names: Muku, Milchvieh, etc.

# For insights command
muka> insights focus=<Tab>
# Shows: outliers  trends  distribution  general
```

## Command History

### Navigate History

- **Up Arrow** (↑) - Previous command
- **Down Arrow** (↓) - Next command
- **Ctrl+R** - Reverse search through history

### Persistent History

Command history is saved to `~/.muka_history` and persists across sessions:

```bash
# Session 1
muka> question How many farms are there?

# Close and reopen client...

# Session 2
# Press Up arrow to get previous command
muka> question How many farms are there?  # Retrieved from history!
```

## Keyboard Shortcuts

### Editing Shortcuts (Emacs-style)

- **Ctrl+A** - Move to beginning of line
- **Ctrl+E** - Move to end of line
- **Ctrl+K** - Delete from cursor to end of line
- **Ctrl+U** - Delete entire line
- **Ctrl+W** - Delete word before cursor
- **Alt+B** - Move back one word
- **Alt+F** - Move forward one word
- **Ctrl+L** - Clear screen (same as `clear` command)

### Navigation

- **Left/Right Arrows** - Move cursor
- **Home** - Beginning of line
- **End** - End of line
- **Ctrl+Left** - Move back one word
- **Ctrl+Right** - Move forward one word

### Special Keys

- **Tab** - Complete command or parameter
- **Ctrl+C** - Cancel current input
- **Ctrl+D** - Exit (same as `quit`)
- **Enter** - Execute command

## Example Session with Tab Completion

```bash
$ ./test-mcp

🐄 MuKa Farm Data Analysis - Interactive MCP Client
Type 'help' for commands, 'quit' to exit
Press Tab for command completion, Ctrl+C to cancel

✓ Configuration loaded
✓ Auto-loaded 34923 farms (7 groups)

muka> qu<Tab>
# Automatically completes to:
muka> query

# Continue typing or press Tab again for parameters
muka> query <Tab>
# Shows: group=  tvd=  year=  min_animals=  max_animals=

# Type 'g' and Tab
muka> query g<Tab>
# Completes to:
muka> query group=

# Press Tab to see group options
muka> query group=<Tab>
# Shows: Muku  Muku_Amme  Milchvieh  BKMmZ  BKMoZ  IKM

# Type 'M' and Tab
muka> query group=M<Tab>
# Shows: Muku  Muku_Amme  Milchvieh

# Type 'u' to narrow down
muka> query group=Mu<Tab>
# Shows: Muku  Muku_Amme

# Select Muku
muka> query group=Muku

Executing: query...
✅ Success
Found 5000 farms
...

# Press Up arrow to get previous command
muka> query group=Muku

# Edit it easily
muka> query group=Milchvieh
```

## Command Examples with Tab Completion

### Query with Multiple Parameters

```bash
muka> query <Tab>
muka> query group=<Tab>
muka> query group=Muku <Tab>
muka> query group=Muku min_animals=<type value>
# Final: query group=Muku min_animals=50
```

### Statistics for Group

```bash
muka> st<Tab>
muka> stats <Tab>
muka> stats group=<Tab>
muka> stats group=Milchvieh
```

### Data Insights

```bash
muka> ins<Tab>
muka> insights <Tab>
muka> insights focus=<Tab>
muka> insights focus=outliers
```

## Fallback Mode

If `prompt_toolkit` is not installed, the client falls back to basic input mode:

```bash
muka> command
```

You'll see a notice:

```
⚠️ Note: Install prompt_toolkit for tab completion: uv add prompt_toolkit
```

The client still works fully, just without:
- Tab completion
- Command history
- In-line editing shortcuts

## Tips and Tricks

### 1. Explore Commands with Tab

Not sure what commands are available? Just press Tab at the empty prompt:

```bash
muka> <Tab>
# Shows all available commands
```

### 2. Quick Parameter Discovery

Want to know what parameters a command accepts? Type the command and press Tab:

```bash
muka> query <Tab>
# Shows: group=  tvd=  year=  min_animals=  max_animals=
```

### 3. Use History for Complex Commands

For long questions, use history instead of retyping:

```bash
muka> question What percentage of farms have more than 100 dairy cows?
# Press Up to recall and modify
muka> question What percentage of farms have more than 200 dairy cows?
```

### 4. Combine with Clear

Keep your terminal clean:

```bash
muka> clear  # or Ctrl+L
# Screen clears, ready for new commands
```

### 5. Quick Exit

Multiple ways to exit:

```bash
muka> quit
muka> exit
muka> q
# Or press: Ctrl+D
```

## Troubleshooting

### Tab completion not working?

1. Check if prompt_toolkit is installed:
   ```bash
   uv pip list | grep prompt_toolkit
   ```

2. Install it:
   ```bash
   ./setup-mcp-client
   ```

3. Restart the client

### History not saving?

Check permissions on history file:
```bash
ls -la ~/.muka_history
chmod 644 ~/.muka_history
```

### Keyboard shortcuts not working?

Make sure your terminal supports ANSI escape sequences. Most modern terminals (iTerm2, Alacritty, Windows Terminal, GNOME Terminal, etc.) work fine.

## Configuration

History file location: `~/.muka_history`

To clear history:
```bash
rm ~/.muka_history
```

To disable history (temporary):
```bash
export MUKA_NO_HISTORY=1
./test-mcp
```

## Technical Details

### Completion Strategy

1. **Command-level**: Matches commands at the start of input
2. **Parameter-level**: Context-aware based on the command
3. **Value-level**: Suggests known values for specific parameters (e.g., group names)

### Supported Completions

| Command    | Parameters                           | Value Completion |
|------------|--------------------------------------|------------------|
| `query`    | group, tvd, year, min/max_animals   | ✅ group names   |
| `stats`    | group                                | ✅ group names   |
| `insights` | focus, group                         | ✅ focus types   |
| `farm`     | tvd                                  | ❌              |
| `aggregate`| group_by, aggregate                  | ❌              |
| `metric`   | expression, filter, group_by         | ❌              |

### Implementation

- **Library**: `prompt_toolkit` for advanced terminal features
- **Completer**: Custom `MukaCompleter` class
- **History**: File-based persistent history
- **Style**: Cyan bold prompt matching Rich theme

---

**Enjoy the enhanced command-line experience!** 🚀 Press Tab and explore!
