# Bug Fix Summary - 2025-10-11

## Issue 1: JSON Serialization Error with numpy types

**Error:** `TypeError: Object of type int64 is not JSON serializable`

**Root Cause:** 
- Pandas operations (like `.sum()`, `.mean()`, etc.) return numpy scalar types (`np.int64`, `np.float64`)
- These types are NOT directly JSON serializable
- The MCP server evaluates pandas expressions directly via `eval()`, bypassing Pydantic models
- While Pydantic v2 handles serialization for model fields, direct pandas operations bypass this

**Example:**
```python
# This returns np.int64, not Python int
result = n_animals_total.between(50,100).sum()
json.dumps({"result": result})  # ❌ TypeError!
```

**Fix:**
Added `to_json_serializable()` helper function that recursively converts:
- `np.int64/int32` → `int`
- `np.float64/float32` → `float`
- `np.bool_` → `bool`
- `np.ndarray` → `list`
- Dictionaries and lists recursively

Applied to all MCP handler return values that process pandas data.

**Why Pydantic doesn't help here:**
- Pydantic models work great when data flows through them
- Direct pandas operations bypass Pydantic entirely
- `eval()` in MCP server executes pandas code directly, returning numpy types

## Issue 2: Column Name Mismatch

**Error:** `KeyError: 'classification_pattern'`

**Root Cause:**
- Code was looking for column named `classification_pattern`
- Actual column name is `group`
- Copy-paste error from old codebase or documentation

**Fix:**
Changed all references from `classification_pattern` to `group` in `handle_compare_groups()`.

## Issue 3: String vs List Parameter Handling

**Error:** `TypeError: only list-like objects are allowed to be passed to isin(), you passed a str`

**Root Cause:**
- MCP tool schema defines `groups` parameter as array
- Interactive client passes comma-separated string: `"Muku,Muku_Amme"`
- Pandas `.isin()` requires a list, not a string

**Fix:**
Added robust parameter handling in `handle_compare_groups()`:
```python
if isinstance(groups_to_compare, str):
    groups_to_compare = [g.strip() for g in groups_to_compare.split(",")]
```

This handles both:
- String format: `"Muku,Muku_Amme"` → splits into list
- List format: `["Muku", "Muku_Amme"]` → uses as-is

Same fix applied to `metrics` parameter.

## Issue 4: Numpy Types in Dictionary String Representation

**Error:** `NotRenderableError: Unable to render ... 'Unclassified': np.int64(14236)`

**Root Cause:**
- `get_group_counts()` returns dict with numpy int64 values from pandas operations
- When dict is converted to string for display: `f"{group_counts}"` 
- String representation includes `np.int64(...)` which breaks Rich rendering
- `.value_counts().to_dict()` and `.sum()` return numpy types, not Python int

**Fix:**
Added explicit conversion in `get_group_counts()`:
```python
counts = {k: int(v) for k, v in counts.items()}
```

This ensures the dictionary contains native Python integers, so string representation is clean.

**Pattern:** Any dict/list that will be stringified for display needs native Python types, not numpy types.

## Issue 5: Dictionary Parameter Parsing

**Error:** `"'{'n_animals_total':'mean'}' is not a valid function for 'DataFrameGroupBy' object"`

**Root Cause:**
- Interactive client passes aggregate parameter as string: `"{'n_animals_total':'mean'}"`
- MCP tool expects dictionary object: `{'n_animals_total': 'mean'}`
- Server was trying to use string directly with pandas `.agg()` method
- Command line parsing doesn't automatically convert dict literals

**Fix:**
Added `ast.literal_eval()` to safely parse dict string:
```python
if isinstance(aggregate, str):
    try:
        import ast
        aggregate = ast.literal_eval(aggregate)
    except (ValueError, SyntaxError) as e:
        return {"error": f"Invalid aggregate format..."}
```

Also added comma-separated string handling for `group_by` parameter.

**Why ast.literal_eval?**
- Safely evaluates Python literals (dict, list, etc.)
- Does NOT execute arbitrary code (secure)
- Standard library solution for this use case

## Issue 6: Rich Can't Render Python Lists

**Error:** `NotRenderableError: Unable to render ['Total farms: 34921', ...]; A str, Segment or object with __rich_console__ method is required`

**Root Cause:**
- Server returns insights as list of strings: `["insight1", "insight2"]`
- Client passes list directly to Rich Panel
- Rich can't render Python list objects - needs string or Rich renderables

**Fix:**
Changed client display code to join list into formatted string:
```python
insights_text = "\n".join(f"• {insight}" for insight in result["insights"])
console.print(Panel(insights_text, title="💡 Data Insights"))
```

**Lesson:** Rich library requires:
- Strings
- Rich objects (Table, Panel, etc.)
- Objects with `__rich_console__` method
- NOT raw Python lists/dicts

## Lessons Learned

1. **Don't assume column names** - verify actual DataFrame schema
2. **Pandas returns numpy types** - always convert for JSON serialization
3. **Pydantic doesn't help with eval()** - direct code execution bypasses validation
4. **Test with real data** - schema mismatches only show up at runtime

## Prevention

- Add unit tests that verify JSON serialization of pandas results
- Add DataFrame schema validation/documentation
- Consider using typed DataFrames (pandera) for compile-time schema checking
- Add integration tests for all MCP handlers
