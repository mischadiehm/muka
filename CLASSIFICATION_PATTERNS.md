# Farm Classification Patterns in MuKa_Betriebe_new.qmd

## Overview

The R/Quarto analysis file uses **4 binary columns** to classify farms into 6 distinct types based on their cattle operations. This classification system uses a pattern-matching approach where each farm type corresponds to a unique combination of presence/absence (1/0) values across these columns.

## Classification Columns

### The Six Key Columns

1. **`1_femaleDairyCattle_V2`** - Presence of female dairy cattle (age 3+)
   - `1` = Has female dairy cattle
   - `0` = No female dairy cattle

2. **`2_femaleCattle`** - Presence of female cattle (total, age 3+)
   - `1` = Has female cattle (non-dairy breeding stock)
   - `0` = No female cattle

3. **`3_calf85Arrivals`** - Significant calf arrivals (<85 days)
   - `1` = Receives calves (buying operation)
   - `0` = Minimal calf arrivals

4. **`5_calf51nonSlaughterLeavings`** - Young calf leavings (<51 days, non-slaughter)
   - `1` = Calves leave farm young (dairy pattern - selling calves)
   - `0` = Calves stay on farm or go directly to slaughter

5. **`6_female731Slaughterings`** - Female slaughterings (<731 days / <24 months)
   - `1` = Has female slaughterings in this age range
   - `0` = No female slaughterings in this age range

6. **`7_young51to730Slaughterings`** - Young animal slaughterings (51-730 days / ~2-24 months)
   - `1` = Has young slaughterings in this age range
   - `0` = No young slaughterings in this age range

## Farm Type Classification Patterns

### Pattern Lookup Table

**NEW 6-Field Classification (Current Implementation):**

```r
group_ref <- data.frame(
  Variable = c("1_femaleDairyCattle_V2", "2_femaleCattle", 
               "3_calf85Arrivals", "5_calf51nonSlaughterLeavings",
               "6_female731Slaughterings", "7_young51to730Slaughterings"),
  Muku            = c(0, 0, 0, 0, 0, 1),
  Muku_Amme       = c(0, 0, 1, 0, 0, 1),
  Milchvieh       = c(1, 0, 0, 1, NA, NA),  # NA = accepts 0 or 1
  BKMmZ           = c(1, 0, 1, 0, 0, 1),
  BKMoZ           = c(1, 0, 0, 0, 0, 1),
  IKM             = c(0, 1, 1, 0, 0, 1)
)
```

### Pattern Explanations

#### 1. **Muku** (Mutterkuhhaltung - Suckler Cow Farming)
**Pattern:** `[0, 0, 0, 0, 0, 1]`

- ❌ No dairy cattle
- ❌ No general female cattle indicator
- ❌ No calf arrivals
- ❌ No young calf leavings
- ❌ No female slaughterings <731 days
- ✅ **Has young slaughterings** (51-730 days)

**Logic:** Pure beef operation where cows raise their own calves to maturity on-farm. Calves stay with mothers and are raised to slaughter weight without early transfers. Young slaughterings indicate raising animals to typical beef slaughter age.

---

#### 2. **Muku_Amme** (Suckler Cow with Nurse Cow/Calf Buying)
**Pattern:** `[0, 0, 1, 0, 0, 1]`

- ❌ No dairy cattle
- ❌ No general female cattle indicator
- ✅ **Has calf arrivals** (buys young calves)
- ❌ No young calf leavings
- ❌ No female slaughterings <731 days
- ✅ **Has young slaughterings** (51-730 days)

**Logic:** Beef operation that BUYS young calves from external sources and raises them to slaughter. The key differentiator from pure Muku is the calf purchases (`3_calf85Arrivals = 1`).

---

#### 3. **Milchvieh** (Dairy Farming)
**Pattern:** `[1, 0, 0, 1, (0||1), (0||1)]` - **FLEXIBLE on fields 5 & 6**

- ✅ **Has dairy cattle** (milking cows)
- ❌ No general female cattle indicator
- ❌ No calf arrivals
- ✅ **Has young calf leavings** (sells calves young)
- ❓ **Any value** for female slaughterings (0 or 1 accepted)
- ❓ **Any value** for young slaughterings (0 or 1 accepted)

**Logic:** Pure dairy operation. Dairy cows produce milk, and calves are sold/transferred young (within 51 days) since they're not needed for beef production. The slaughter patterns can vary depending on whether the farm occasionally slaughters culled dairy cows or keeps some animals longer. This is the classic dairy pattern: keep cows for milk, sell calves early.

**Note:** This group accepts 4 different patterns: `[1,0,0,1,0,0]`, `[1,0,0,1,0,1]`, `[1,0,0,1,1,0]`, `[1,0,0,1,1,1]`

---

#### 4. **BKMmZ** (Beef-Dairy Combined WITH Calf Purchase - "mit Zukauf")
**Pattern:** `[1, 0, 1, 0, 0, 1]`

- ✅ **Has dairy cattle**
- ❌ No general female cattle indicator
- ✅ **Has calf arrivals** (buys calves)
- ❌ No young calf leavings
- ❌ No female slaughterings <731 days
- ✅ **Has young slaughterings** (51-730 days)

**Logic:** Combined operation with dairy cattle that also BUYS calves to raise for beef. Calves stay on farm (not sold young) and are raised to slaughter. This combines milk production with calf fattening using purchased animals.

---

#### 5. **BKMoZ** (Beef-Dairy Combined WITHOUT Calf Purchase - "ohne Zukauf")
**Pattern:** `[1, 0, 0, 0, 0, 1]`

- ✅ **Has dairy cattle**
- ❌ No general female cattle indicator
- ❌ No calf arrivals
- ❌ No young calf leavings
- ❌ No female slaughterings <731 days
- ✅ **Has young slaughterings** (51-730 days)

**Logic:** Combined operation with dairy cattle that raises its OWN calves for beef. Unlike pure dairy (Milchvieh), these farms keep calves to raise for meat. No external calf purchases needed.

---

#### 6. **IKM** (Intensiv-Kälbermast - Intensive Calf Fattening)
**Pattern:** `[0, 1, 1, 0, 0, 1]`

- ❌ No dairy cattle
- ✅ **Has female cattle** (different breeding stock)
- ✅ **Has calf arrivals** (buys calves)
- ❌ No young calf leavings
- ❌ No female slaughterings <731 days
- ✅ **Has young slaughterings** (51-730 days)

**Logic:** Specialized calf fattening operation. Buys young calves and raises them to slaughter weight. Uses female cattle but NOT for dairy (possibly for breeding or as nurse cows). This is an intensive buying-and-fattening operation.

---

## Classification Logic in Code

The classification uses R's `case_when()` function with exact pattern matching:

```r
group = case_when(
  # Muku: All zeros - pure suckler cow
  `1_femaleDairyCattle_V2` == 0 & `2_femaleCattle` == 0 & 
  `3_calf85Arrivals` == 0 & `5_calf51nonSlaughterLeavings` == 0 
  ~ "Muku",
  
  # Muku_Amme: Only calf arrivals
  `1_femaleDairyCattle_V2` == 0 & `2_femaleCattle` == 0 & 
  `3_calf85Arrivals` == 1 & `5_calf51nonSlaughterLeavings` == 0
  ~ "Muku_Amme",
  
  # Milchvieh: Dairy + young calf leavings
  `1_femaleDairyCattle_V2` == 1 & `2_femaleCattle` == 0 & 
  `3_calf85Arrivals` == 0 & `5_calf51nonSlaughterLeavings` == 1
  ~ "Milchvieh",
  
  # BKMmZ: Dairy + calf arrivals
  `1_femaleDairyCattle_V2` == 1 & `2_femaleCattle` == 0 & 
  `3_calf85Arrivals` == 1 & `5_calf51nonSlaughterLeavings` == 0
  ~ "BKMmZ",
  
  # BKMoZ: Only dairy
  `1_femaleDairyCattle_V2` == 1 & `2_femaleCattle` == 0 & 
  `3_calf85Arrivals` == 0 & `5_calf51nonSlaughterLeavings` == 0
  ~ "BKMoZ",
  
  # IKM: Female cattle + calf arrivals
  `1_femaleDairyCattle_V2` == 0 & `2_femaleCattle` == 1 & 
  `3_calf85Arrivals` == 1 & `5_calf51nonSlaughterLeavings` == 0
  ~ "IKM",
  
  # Unmatched patterns
  TRUE ~ NA_character_
)
```

## Key Insights

### 1. **Mutually Exclusive Patterns**
Each farm type has a UNIQUE 4-digit binary pattern, ensuring no overlap in classification. This is critical for accurate categorization.

### 2. **Restored Slaughter Columns**
The current implementation uses **6 classification columns**. Previously, the R code had commented out slaughter-related columns, but they have been restored:
- ✅ `6_female731Slaughterings` - Female slaughterings (51-730 days / ~2-24 months) - **NOW ACTIVE**
- ✅ `7_young51to730Slaughterings` - Young animal slaughterings (51-730 days) - **NOW ACTIVE**
- ❌ `4_maleCalf85Arrivals` - Male calf arrivals - Still not used

The classification evolved from 4 columns (simplified version in R) to **6 columns** (current Python implementation) for more precise farm type differentiation.

### 3. **Business Logic Encoding**
The patterns encode key business characteristics:
- **Dairy presence** (`column 1`) - Is this a milking operation?
- **Calf buying** (`column 3`) - Does the farm purchase external calves?
- **Calf selling** (`column 5`) - Does the farm sell calves young?
- **Female cattle type** (`column 2`) - Non-dairy breeding stock?

### 4. **Pattern Completeness**
With 6 binary columns, there are 2^6 = 64 possible combinations. Only 6-9 patterns are used for classification (Milchvieh accepts 4 variants due to flexible fields 5&6), meaning most combinations result in `NA` (unclassified). This suggests:
- Some combinations are rare/invalid in practice
- The system is designed for specific Swiss cattle farming operations
- Unmatched farms may be mixed operations or outliers
- The flexible matching for Milchvieh (fields 5&6 = any value) accounts for varying slaughter patterns in dairy operations

## Comparison with Python Implementation

The Python code in this project (`muka_analysis/classifier.py`) implements the SAME pattern-matching logic with 6 fields:

```python
CLASSIFICATION_PATTERNS = {
    "Muku":       [0, 0, 0, 0, 0, 1],
    "Muku_Amme":  [0, 0, 1, 0, 0, 1],
    "Milchvieh":  [1, 0, 0, 1, None, None],  # None = accepts any value (0 or 1)
    "BKMmZ":      [1, 0, 1, 0, 0, 1],
    "BKMoZ":      [1, 0, 0, 0, 0, 1],
    "IKM":        [0, 1, 1, 0, 0, 1],
}
```

**Field Mapping:**
1. `indicator_female_dairy_cattle_v2` ← `1_femaleDairyCattle_V2`
2. `indicator_female_cattle` ← `2_femaleCattle`
3. `indicator_calf_arrivals` ← `3_calf85Arrivals`
4. `indicator_calf_leavings` ← `5_calf51nonSlaughterLeavings`
5. `indicator_female_slaughterings` ← `6_female731Slaughterings`
6. `indicator_young_slaughterings` ← `7_young51to730Slaughterings`

## Summary Statistics

The analysis also computes summary statistics for each classified group:
- Total animal counts
- Female dairy cattle metrics (counts, days, proportions)
- Arrival and leaving patterns
- Slaughtering statistics
- Age group distributions

This validates that the classification produces meaningful groups with distinct operational characteristics.
