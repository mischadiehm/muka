# MuKa MCP Tools - Quick Reference Guide

Complete reference for all MCP server tools with practical examples.

## 🚀 Quick Start

```bash
# Start the interactive client
uv run python interactive_mcp_client.py

# See all examples in the client
> examples

# View this guide
cat MCP_TOOLS_REFERENCE.md
```

## 📋 Table of Contents

1. [Data Management](#1-data-management)
2. [Query & Filter](#2-query--filter)
3. [Farm Details](#3-farm-details)
4. [Statistical Analysis](#4-statistical-analysis)
5. [Group Comparison](#5-group-comparison)
6. [Natural Language Questions](#6-natural-language-questions)
7. [Data Insights](#7-data-insights)
8. [Custom Metrics](#8-custom-metrics)
9. [Aggregations](#9-aggregations)
10. [Export](#10-export)

---

## 1. Data Management

### `info` - Get Data Status

Check current data state (loaded, classified, counts).

**Example:**

```bash
muka> info
```

**Returns:**

```json
{
  "loaded": true,
  "classified": true,
  "total_rows": 34923,
  "group_counts": {
    "Muku": 12450,
    "Milchvieh": 15230,
    "BKMmZ": 3200,
    "BKMoZ": 2100,
    "Muku_Amme": 1543,
    "IKM": 400
  }
}
```

### `load` - Reload Data

Reload data from CSV (usually not needed - auto-loaded at startup).

**Example:**

```bash
muka> load
```

### `classify` - Re-classify Farms

Re-run classification (usually not needed - auto-classified).

**Example:**

```bash
muka> classify
```

---

## 2. Query & Filter

### `query` - Filter Farms

Query farms with flexible filters: group, tvd, year, min_animals, max_animals.

**Example 1: All Muku farms**

```bash
muka> query group=Muku
```

**Example 2: Large dairy farms (>100 animals)**

```bash
muka> query group=Milchvieh min_animals=100
```

**Example 3: Medium-sized farms (50-100 animals)**

```bash
muka> query min_animals=50 max_animals=100
```

**Example 4: Specific farm by TVD ID**

```bash
muka> query tvd=123456
```

**Example 5: Farms from specific year**

```bash
muka> query year=2024
```

**Available Groups:**

- `Muku` - Mother cow farms
- `Muku_Amme` - Mother cow farms with nurse cows
- `Milchvieh` - Dairy farms
- `BKMmZ` - Combined dairy with breeding
- `BKMoZ` - Combined dairy without breeding
- `IKM` - Intensive calf rearing

---

## 3. Farm Details

### `farm` - Get Detailed Farm Information

Get complete details for a specific farm by TVD ID.

**Example:**

```bash
muka> farm tvd=123456
```

**Returns:**

- Classification indicators
- Animal counts (total, dairy, calves, etc.)
- Calf movements (arrivals, leavings)
- Proportions and derived metrics
- Group assignment

---

## 4. Statistical Analysis

### `stats` - Calculate Group Statistics

Calculate comprehensive statistics (min, max, mean, median) for all numeric fields.

**Example 1: All groups statistics**

```bash
muka> stats
```

**Example 2: Dairy farms only**

```bash
muka> stats group=Milchvieh
```

**Example 3: Muku farms statistics**

```bash
muka> stats group=Muku
```

**Returns:**

Statistical summary with min, max, mean, and median for:

- Animal counts
- Dairy cattle proportions
- Calf movements
- Slaughter proportions
- And all other numeric fields

---

## 5. Group Comparison

### `compare` - Compare Farm Groups

Side-by-side comparison of key metrics between farm groups.

**Example 1: Compare all groups**

```bash
muka> compare
```

**Example 2: Compare specific groups (coming soon)**

```bash
muka> compare groups=Muku,Milchvieh
```

**Shows:**

- Total animals
- Dairy cattle counts
- Calf arrivals and leavings
- Female cattle statistics
- Other key metrics

---

## 6. Natural Language Questions

### `question` - Ask in Natural Language

Ask questions about your data in plain English - the system will parse and answer.

**Example 1: Count farms**

```bash
muka> question How many dairy farms are there?
```

**Example 2: Percentages**

```bash
muka> question What percentage of farms are Muku?
```

**Example 3: Averages**

```bash
muka> question What is the average animal count?
```

**Example 4: Group comparisons**

```bash
muka> question Which group has the highest average animals?
```

**Example 5: Outliers**

```bash
muka> question Are there farms with unusual animal counts?
```

**Supported Question Types:**

- Counts: "How many...", "Count..."
- Percentages: "What percentage...", "What percent..."
- Averages: "What is the average...", "Mean..."
- Comparisons: "Which group has...", "Compare..."
- Outliers: "Unusual...", "Outliers..."

---

## 7. Data Insights

### `insights` - Generate Data Insights

Automated pattern detection and analysis.

**Example 1: General insights**

```bash
muka> insights
muka> insights focus=general
```

**Example 2: Find outliers**

```bash
muka> insights focus=outliers
```

**Example 3: Data distribution**

```bash
muka> insights focus=distribution
```

**Example 4: Group-specific insights**

```bash
muka> insights group=Milchvieh
```

**Focus Options:**

- `general` - Overall data patterns
- `outliers` - Unusual values
- `trends` - Trends over time
- `distribution` - Data distribution analysis

---

## 8. Custom Metrics

### `metric` - Calculate Custom Metrics

Calculate custom metrics using pandas-style expressions.

**Example 1: Sum all animals**

```bash
muka> metric expression=n_animals_total.sum()
```

**Example 2: Average animals per farm**

```bash
muka> metric expression=n_animals_total.mean()
```

**Example 3: Count large farms (>100 animals)**

```bash
muka> metric expression=(n_animals_total>100).sum()
```

**Example 4: Farms in range (50-100 animals)**

```bash
muka> metric expression=n_animals_total.between(50,100).sum()
```

**Example 5: Statistical summary**

```bash
muka> metric expression=n_animals_total.describe()
```

**Example 6: Complex conditions**

```bash
muka> metric expression=((n_animals_total>20)&(n_animals_total<=50)).sum()
```

**Example 7: Small farms**

```bash
muka> metric expression=n_animals_total.lt(20).sum()
```

**Example 8: Very large farms**

```bash
muka> metric expression=n_animals_total.gt(500).sum()
```

**Supported Patterns:**

- Column operations: `column_name.sum()`, `column_name.mean()`, `column_name.median()`
- Comparisons: `(column_name > value).sum()`, `(column_name < value).sum()`
- Between: `column_name.between(min, max).sum()`
- Methods: `column_name.gt(value)`, `column_name.lt(value)`, `column_name.eq(value)`
- Boolean ops: `&` (and), `|` (or), `~` (not)
- Statistical: `column_name.describe()`, `column_name.quantile(0.95)`

**Available Columns:**

All numeric columns from the farm data can be used directly:

- `n_animals_total`
- `n_females_age3_dairy`
- `n_females_age3_total`
- `n_females_younger731`
- `n_animals_from51_to730`
- `n_total_entries_younger85`
- `n_total_leavings_younger51`
- `prop_days_female_age3_dairy`
- `prop_females_slaughterings_younger731`
- And many more...

---

## 9. Aggregations

### `aggregate` - Aggregate Data by Fields

Group and aggregate data with various operations.

**Note:** Currently requires Python dict syntax - to be simplified in future versions.

**Operations:**

- `sum` - Sum values
- `mean` - Average values
- `median` - Median values
- `min` - Minimum value
- `max` - Maximum value
- `count` - Count records

**Example (conceptual):**

```python
# Total animals by group
aggregate(group_by=['group'], aggregate={'n_animals_total': 'sum'})

# Average by year and group
aggregate(group_by=['year', 'group'], aggregate={'n_animals_total': 'mean'})
```

---

## 10. Export

### `export` - Export Results to Excel

Export analysis results to Excel file with multiple sheets.

**Example 1: Default export**

```bash
muka> export
```

Saves to: `output/analysis_summary.xlsx`

**Example 2: Custom filename**

```bash
muka> export my_analysis.xlsx
```

**Exported Sheets:**

- Summary statistics by group
- Detailed farm-level data
- Group counts and distributions
- Classification patterns

---

## 💡 Tips & Best Practices

1. **Start with `info`** to check data status
2. **Use `stats`** to understand overall patterns before diving deeper
3. **Try `question`** for quick answers in natural language
4. **Use `query`** to filter and explore specific subsets of farms
5. **Use `metric`** for custom pandas calculations on the data
6. **Use `insights`** to discover patterns you might miss manually
7. **Export results** with `export` for further analysis in Excel
8. **Type `help`** anytime for a quick command overview
9. **Use `examples`** in the interactive client to see all examples
10. **Tab completion** is available for commands and parameters!

---

## 🔧 Advanced Usage

### Chaining Analysis

You can perform multiple analyses in sequence:

```bash
# 1. Check status
muka> info

# 2. Get general insights
muka> insights focus=general

# 3. Query specific group
muka> query group=Milchvieh min_animals=100

# 4. Get detailed statistics
muka> stats group=Milchvieh

# 5. Export results
muka> export dairy_farms_analysis.xlsx
```

### Custom Metric Patterns

**Count by size categories:**

```bash
# Very small (<20 animals)
muka> metric expression=n_animals_total.lt(20).sum()

# Small (20-50)
muka> metric expression=((n_animals_total>=20)&(n_animals_total<50)).sum()

# Medium (50-100)
muka> metric expression=n_animals_total.between(50,100).sum()

# Large (100-500)
muka> metric expression=((n_animals_total>=100)&(n_animals_total<500)).sum()

# Very large (>500)
muka> metric expression=n_animals_total.gt(500).sum()
```

**Percentile analysis:**

```bash
# 95th percentile
muka> metric expression=n_animals_total.quantile(0.95)

# IQR (Interquartile Range)
muka> metric expression=n_animals_total.quantile(0.75)-n_animals_total.quantile(0.25)
```

---

## 🏷️ Farm Classifications Reference

### Group Definitions

**Muku (Mother Cow Farms)**

- No dairy cattle indicators
- Female cattle present
- Minimal calf movements

**Muku_Amme (Mother Cow with Nurse Cows)**

- Similar to Muku but with calf rearing characteristics
- Higher calf arrival rates

**Milchvieh (Dairy Farms)**

- Strong dairy cattle indicators
- Female dairy cattle present
- Regular dairy operations

**BKMmZ (Combined Dairy with Breeding)**

- Dairy operations combined with breeding
- Both dairy and calf rearing indicators

**BKMoZ (Combined Dairy without Breeding)**

- Dairy operations with limited breeding
- Dairy indicators without strong breeding patterns

**IKM (Intensive Calf Rearing)**

- High calf arrival rates
- High calf leaving rates
- Specialized in raising calves

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Data not loaded or classified"**

- Run `info` to check status
- Data should auto-load at startup
- If needed, run `load` then `classify`

**Issue: "Unknown group"**

- Check spelling - group names are case-sensitive
- Valid groups: Muku, Muku_Amme, Milchvieh, BKMmZ, BKMoZ, IKM

**Issue: Metric expression fails**

- Ensure column name is correct (case-sensitive)
- Use parentheses for complex conditions
- Check pandas syntax for operations

**Issue: No results from query**

- Check filter criteria - might be too restrictive
- Use `info` to see available data ranges
- Try removing some filters

---

## 📚 Additional Resources

- **[README.md](README.md)** - Project overview
- **[USAGE.md](USAGE.md)** - Detailed usage guide
- **[MCP_QUICKSTART.md](MCP_QUICKSTART.md)** - MCP setup guide
- **[MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)** - Complete MCP reference
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Configuration system

---

## 🎯 Interactive Client Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `examples` | Show all examples ⭐ | `examples` |
| `info` | Data status | `info` |
| `load` | Reload data | `load` |
| `classify` | Re-classify | `classify` |
| `query` | Filter farms | `query group=Muku` |
| `farm` | Farm details | `farm tvd=123456` |
| `stats` | Statistics | `stats group=Milchvieh` |
| `compare` | Compare groups | `compare` |
| `question` | Natural language | `question How many dairy farms?` |
| `insights` | Find patterns | `insights focus=outliers` |
| `metric` | Custom calc | `metric expression=n_animals_total.mean()` |
| `aggregate` | Group & aggregate | (Python dict syntax) |
| `export` | Export to Excel | `export results.xlsx` |
| `help` | Show commands | `help` |
| `clear` | Clear screen | `clear` |
| `quit` | Exit | `quit` or `exit` |

---

**Last Updated:** October 2025  
**Version:** 1.0.0
