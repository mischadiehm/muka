# Classification Mode Comparison: 4 vs 6 Indicators

## Overview

The MuKa farm classification tool now supports two classification modes:

- **NEW Method (6 indicators)**: Uses all 6 binary indicators including slaughter fields
- **OLD Method (4 indicators)**: Uses only the first 4 indicators, ignoring slaughter patterns

## Quick Usage

```bash
# Use 6-indicator mode (default - NEW method)
uv run python -m muka_analysis analyze

# Use 4-indicator mode (OLD method)
uv run python -m muka_analysis analyze --use-4-indicators
```

## Configuration

You can also set the default mode in `muka_config.toml`:

```toml
[classification]
use_six_indicators = true  # Set to false for 4-indicator mode
```

## Comparison Results

Based on the test dataset (34,921 farms):

| Mode | Classified Farms | Unclassified Farms | Classification Rate |
|------|------------------|-------------------|---------------------|
| **6-indicator (NEW)** | 20,685 | 14,236 | 59.2% |
| **4-indicator (OLD)** | 25,940 | 8,981 | 74.3% |

### Group Distribution Comparison

#### 6-Indicator Mode (NEW)

| Farm Group | Count | Avg Animals | Median Animals | Avg Females 3+ | Median Females 3+ |
|------------|-------|-------------|----------------|----------------|-------------------|
| Muku       | 4,086 | 56.1        | 42.0           | 21.4           | 16.0              |
| Muku_Amme  | 1,461 | 95.5        | 72.0           | 26.4           | 23.0              |
| Milchvieh  | 12,006| 91.0        | 75.0           | 45.8           | 37.0              |
| BKMmZ      | 1,183 | 95.0        | 74.0           | 28.0           | 22.0              |
| BKMoZ      | 1,309 | 92.5        | 62.0           | 51.9           | 29.0              |
| IKM        | 640   | 238.1       | 153.0          | 0.5            | 0.0               |

#### 4-Indicator Mode (OLD)

| Farm Group | Count | Avg Animals | Median Animals | Avg Females 3+ | Median Females 3+ |
|------------|-------|-------------|----------------|----------------|-------------------|
| Muku       | 6,069 | 51.7        | 39.0           | 20.6           | 15.0              |
| Muku_Amme  | 1,820 | 92.2        | 68.0           | 26.5           | 22.0              |
| Milchvieh  | 12,006| 91.0        | 75.0           | 45.8           | 37.0              |
| BKMmZ      | 1,460 | 95.1        | 72.5           | 29.3           | 22.0              |
| BKMoZ      | 3,776 | 67.1        | 45.0           | 35.5           | 22.0              |
| IKM        | 809   | 220.1       | 137.0          | 0.5            | 0.0               |

### Key Differences

The main differences between the two modes:

1. **Muku**: 4-indicator mode classifies 1,983 more farms (+48.5%)
2. **Muku_Amme**: 4-indicator mode classifies 359 more farms (+24.6%)
3. **Milchvieh**: Same count in both modes (12,006 farms)
4. **BKMmZ**: 4-indicator mode classifies 277 more farms (+23.4%)
5. **BKMoZ**: 4-indicator mode classifies 2,467 more farms (+188.5%)
6. **IKM**: 4-indicator mode classifies 169 more farms (+26.4%)

## Technical Details

### 6-Indicator Classification Patterns

Uses all 6 fields:
1. Female dairy cattle (1_femaleDairyCattle_V2)
2. Other female cattle (2_femaleCattle)
3. Calf arrivals <85 days (3_calf85Arrivals)
4. Calf leavings <51 days (5_calf51nonSlaughterLeavings)
5. **Female slaughterings <731 days (6_female731Slaughterings)**
6. **Young slaughterings 51-730 days (7_young51to730Slaughterings)**

Example patterns:
- Muku: [0, 0, 0, 0, **0, 1**]
- Muku_Amme: [0, 0, 1, 0, **0, 1**]
- Milchvieh: [1, 0, 0, 1, **(0||1), (0||1)**] - accepts any value for fields 5&6
- BKMmZ: [1, 0, 1, 0, **0, 1**]
- BKMoZ: [1, 0, 0, 0, **0, 1**]
- IKM: [0, 1, 1, 0, **0, 1**]

### 4-Indicator Classification Patterns

Uses only first 4 fields (ignores slaughter indicators):
1. Female dairy cattle (1_femaleDairyCattle_V2)
2. Other female cattle (2_femaleCattle)
3. Calf arrivals <85 days (3_calf85Arrivals)
4. Calf leavings <51 days (5_calf51nonSlaughterLeavings)
5. ~~Female slaughterings <731 days~~ **→ IGNORED (any value accepted)**
6. ~~Young slaughterings 51-730 days~~ **→ IGNORED (any value accepted)**

Example patterns (last two fields ignored):
- Muku: [0, 0, 0, 0, **\*, \***]
- Muku_Amme: [0, 0, 1, 0, **\*, \***]
- Milchvieh: [1, 0, 0, 1, **\*, \***]
- BKMmZ: [1, 0, 1, 0, **\*, \***]
- BKMoZ: [1, 0, 0, 0, **\*, \***]
- IKM: [0, 1, 1, 0, **\*, \***]

## When to Use Each Mode

### Use 6-Indicator Mode (NEW - Default) When:

✅ You want the most precise classification  
✅ Slaughter patterns are important for your research  
✅ You need to match the current R code implementation  
✅ You want to distinguish farms based on their complete behavior patterns  
✅ You're performing new analyses that should follow current best practices

### Use 4-Indicator Mode (OLD) When:

✅ You want broader classification with fewer unclassified farms  
✅ Slaughter behavior patterns are not relevant to your analysis  
✅ You need backward compatibility with older analyses  
✅ You want to ignore slaughter-related indicators  
✅ You're comparing with historical data that didn't use slaughter fields

## Implementation Details

The classification mode is controlled by:

1. **Command-line flag**: `--use-4-indicators` (overrides configuration)
2. **Configuration file**: `use_six_indicators` in `[classification]` section
3. **Default**: 6-indicator mode (NEW method)

The classifier automatically adjusts the matching logic:
- In 6-indicator mode: Fields 5 & 6 must match the profile (or be flexible if profile allows)
- In 4-indicator mode: Fields 5 & 6 are set to `None` (accept any value)

## Examples

### Compare Both Modes

```bash
# Run with 6 indicators (default)
uv run python -m muka_analysis analyze --force --save-analysis \
    --excel output/analysis_6indicators.xlsx

# Run with 4 indicators
uv run python -m muka_analysis analyze --force --save-analysis \
    --use-4-indicators \
    --excel output/analysis_4indicators.xlsx
```

### See Unclassified Farms

```bash
# With 6 indicators
uv run python -m muka_analysis analyze --show-unclassified

# With 4 indicators
uv run python -m muka_analysis analyze --use-4-indicators --show-unclassified
```

## Recommendations

**For New Analyses**: Use the default 6-indicator mode unless you have a specific reason to use 4 indicators.

**For Comparative Studies**: Document which mode you used in your methodology, as the results differ significantly (especially for Muku and BKMoZ groups).

**For Production Use**: Consider your research questions:
- If slaughter patterns matter → use 6 indicators
- If you just need broad categorization → use 4 indicators

## See Also

- [CLASSIFICATION_PATTERNS.md](CLASSIFICATION_PATTERNS.md) - Detailed explanation of classification patterns
- [USAGE.md](USAGE.md) - Complete usage guide
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Configuration options
