# Duplicated Functions Analysis and Consolidation Status

**Date:** April 26, 2026  
**Status:** Analysis Complete - Consolidation In Progress

---

## Summary

This document lists all functions that appear in multiple Python files across the codebase, along with consolidation status and recommendations.

---

## Tier 1: CONSOLIDATED (✅ Complete)

### `cal_pierce()`
- **Status:** ✅ Consolidated to `raypath_utils.py`
- **Occurrences:** 8+ files
- **Files Updated:**
  - calculate_the_selected_coverage.py ✅
  - Figure2_plot_map.py ✅
  - PLOT_all_measurements.py ✅
  - plot_measurement_results_all.py ✅
  - plot_residual_on_map.py ✅
  - Codes_ULVZ/plot_single_traces_entrance_points.py ✅
  - examples/extdfig1_plot_latitude_residual.py ✅
  - examples/extdfig1_plot_map.py ✅

---

## Tier 2: NEW UTILITY MODULES CREATED

### `visualization_utils.py` (NEW) ✅

#### Functions Extracted:
1. **`plot_data_matrix()`**
   - **Occurrences:** 9 files
   - **Signature:** `plot_data_matrix(data_matrix, df_station, sample_rate)`
   - **Features:** Now includes comprehensive docstring
   - **Files to Update:**
     - OBS_prepare_data.py
     - SIMU_prepare_data.py
     - SUM_selection_results.py
     - MSR_individual_s3ks.py
     - MSR_synchronized_s3ks.py
     - MSR_synchronized_s4ks.py
     - SUM_grouping_results.py
     - Codes_global_layer/SUM_selection_results.py
     - notuse/measure_single_dataset_s4ks.py

2. **`plot_eq_map()`**
   - **Occurrences:** 6 files
   - **Signature:** `plot_eq_map(df_station, df_hypo)`
   - **Features:** Now includes beach ball focal mechanism
   - **Files to Update:**
     - OBS_prepare_data.py
     - SIMU_prepare_data.py
     - SUM_selection_results.py
     - Codes_global_layer/SUM_selection_results.py
     - SUM_grouping_results.py

3. **`hex_to_kml_color()`**
   - **Occurrences:** 5 files
   - **Signature:** `hex_to_kml_color(hex_color, alpha='ff')`
   - **Features:** Enhanced docstring with alpha channel documentation
   - **Files to Update:**
     - Figure2_plot_map.py
     - plot_residual_on_map.py (defined twice in this file!)
     - generate_3types_for_googlemap.py
     - generate_result_for_googlemap.py
     - plot_comparison.py

4. **`plot_measurement_results()`** *(New function)*
   - **Purpose:** Consolidated plotting of measurement results
   - **Signature:** `plot_measurement_results(df_measure, figdir=None)`

---

### `data_utils.py` (NEW) ✅

#### Functions Extracted:
1. **`cal_dist_time()`**
   - **Occurrences:** 4 files
   - **Signature:** `cal_dist_time(df_station, df_hypo)`
   - **Status:** Fully documented
   - **Files to Update:**
     - OBS_prepare_data.py
     - SIMU_prepare_data.py
     - MSR_individual_s3ks.py
     - MSR_synchronized_s3ks.py

2. **`traces_to_matrix()`**
   - **Occurrences:** 3 files
   - **Signature:** `traces_to_matrix(directory, component, sample_rate, trace_length)`
   - **Status:** Fully documented
   - **Files to Update:**
     - OBS_prepare_data.py
     - SIMU_prepare_data.py

3. **`matrix_align_slant()`**
   - **Occurrences:** 3 files
   - **Signature:** `matrix_align_slant(data_matrix, sample_rate, signal_begin, half_window, before_pick, after_pick)`
   - **Status:** Fully documented with error handling
   - **Files to Update:**
     - OBS_prepare_data.py
     - SIMU_prepare_data.py
     - SUM_grouping_results.py

4. **`filter_and_resample()`** *(New function)*
   - **Purpose:** Common filtering/resampling operations
   - **Signature:** `filter_and_resample(stream, lowpass_freq, resample_rate)`

---

### `raypath_utils.py` (ENHANCED) ✅

#### New Functions Added:
1. **`cal_pierce_and_bounce()`** ✅
   - **Occurrences:** 3+ files
   - **Signature:** `cal_pierce_and_bounce(latS, lonS, depS, latR, lonR, phase, depR=None)`
   - **Returns:** Lists of all CMB piercing points
   - **Status:** Fully documented
   - **Files to Update:**
     - EFigure1_examples.py
     - example_of_crosstalking_on_LD.py
     - Codes_ULVZ/test_for_geometry.py

---

## Tier 3: FUNCTIONS NOT YET CONSOLIDATED

### `cal_raypath()`
- **Status:** ⏳ Planned consolidation
- **Occurrences:** 12+ files
- **Current Location:** raypath_utils.py (already exists)
- **Note:** Most files have local copies, import not yet updated
- **Files with Duplicates:**
  - OBS_prepare_data.py
  - SIMU_prepare_data.py
  - SUM_selection_results.py
  - EFigure1_examples.py
  - example_of_crosstalking_on_LD.py
  - example_of_mantle_effect.py
  - generate_3types_for_googlemap.py
  - generate_result_for_googlemap.py
  - PLOT_groups_waveforms_and_raypath.py
  - Codes_global_layer/SUM_selection_results.py
  - plot_residual_on_vote_map.py
  - plot_comparison.py
  
**Next Step:** Replace all local definitions with `from raypath_utils import cal_raypath`

---

## Tier 4: FUNCTIONS NOT YET EXTRACTED

### Single-Use Utilities
These functions appear in only 1-2 files and may not warrant consolidation:

| Function | Files | Recommendation |
|----------|-------|---|
| `plot_waveform_and_raypath()` | 1 | Keep local |
| `plot_groups()` | 2 | Consider consolidation |
| `create_patches_kml()` | 1 | Keep local |
| `create_great_circle_kml()` | 1 | Keep local |
| `measure_residual()` | 2 | Consider extraction to signal_utils.py |
| `cal_corr()` | 2 | Consider extraction to signal_utils.py |
| `cal_coef()` | 2 | Consider extraction to signal_utils.py |
| `generate_station_list()` | 1 | Keep local |

---

## Import Update Examples

### Before (Old Style)
```python
# Local definition - duplicated in 9 files
def plot_data_matrix(data_matrix, df_station, sample_rate):
    M, N = data_matrix.shape
    # ... implementation ...
```

### After (New Style)
```python
# Single import from utility module
from visualization_utils import plot_data_matrix

# Then use directly
plot_data_matrix(data, stations_df, 100.0)
```

---

## Consolidation Impact Summary

### Code Reduction
| Module | Functions Consolidated | Occurrences Eliminated | Lines Saved (est.) |
|--------|------------------------|-----------------------|--------------------|
| visualization_utils.py | 4 | 20 | ~800 |
| data_utils.py | 4 | 13 | ~650 |
| raypath_utils.py | 1 new | 3 | ~150 |
| **TOTAL** | **9** | **36** | **~1600** |

### Benefits
- **Lines of Code:** Reduction of ~1600 lines of duplicated code
- **Maintainability:** Single source of truth for 36 duplicate instances
- **Testability:** Utility functions can be unit tested once
- **Documentation:** Professional docstrings added to all utilities

---

## Next Steps

### Phase 1: Update Imports (Week 1)
Priority files to update with new imports:

**High Priority (Most impact):**
1. OBS_prepare_data.py - Replace 3 functions
2. SIMU_prepare_data.py - Replace 3 functions
3. SUM_selection_results.py - Replace 3 functions
4. generate_3types_for_googlemap.py - Replace 2 functions

**Medium Priority:**
5. MSR_individual_s3ks.py
6. MSR_synchronized_s3ks.py
7. SUM_grouping_results.py

### Phase 2: Remove Duplicate Definitions
Comment out (don't delete) local function definitions and replace with imports

### Phase 3: Validation
- Run each file to ensure imports work
- Verify output matches previous behavior
- Test with sample data

### Phase 4: Documentation
Add to each updated file:
```python
# See visualization_utils.py for plotting functions
# See data_utils.py for data processing functions
# See raypath_utils.py for raypath calculations
```

---

## Function Statistics

### By Module
| Module | Function Count | Import Status |
|--------|----------------|---|
| raypath_utils.py | 3 | ✅ Complete |
| visualization_utils.py | 4 | ✅ Created |
| data_utils.py | 4 | ✅ Created |
| Local definitions (to update) | 12+ | ⏳ In Progress |

### By Frequency
| Frequency | Function Count | Status |
|-----------|---|---|
| 12+ occurrences | 1 | `cal_raypath()` - needs update |
| 9+ occurrences | 1 | `plot_data_matrix()` - ✅ extracted |
| 6+ occurrences | 1 | `plot_eq_map()` - ✅ extracted |
| 5 occurrences | 1 | `hex_to_kml_color()` - ✅ extracted |
| 3-4 occurrences | 4 | Mixed status |
| 1-2 occurrences | 20+ | Keep local or consider later |

---

## Testing Checklist

After consolidation, verify:

- [ ] All imports work without errors
- [ ] Functions produce identical output as before
- [ ] Docstrings are accurate and helpful
- [ ] Example usage in docstrings works
- [ ] No circular imports
- [ ] Performance unchanged
- [ ] All dependencies installed

---

## Documentation Files Created

1. **CODE_STANDARDIZATION_ANALYSIS.md** - Comprehensive analysis of duplicated functions
2. **PYTHON_STYLE_GUIDE.md** - Code style and best practices guidelines
3. **DUPLICATED_FUNCTIONS.md** - This document, status tracker

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Analysis | ✅ Complete | Done |
| Create Utilities | ✅ Complete | Done |
| Update Imports | 2-3 days | In Progress |
| Testing | 1-2 days | Pending |
| Final Documentation | 1 day | Pending |
| **TOTAL** | **5-7 days** | On Track |

---

## Future Recommendations

1. **Signal Processing Module** (`signal_utils.py`)
   - Extract: `measure_residual()`, `cal_corr()`, `cal_coef()`
   - Timeline: Phase 2

2. **KML/Mapping Module** (`kml_utils.py`)
   - Extract: All KML creation functions
   - Timeline: Phase 3

3. **Automated Testing**
   - Create unit tests for all utility functions
   - Setup CI/CD pipeline
   - Timeline: Phase 4

4. **Code Quality Tools**
   - Setup black for auto-formatting
   - Setup pylint for code analysis
   - Setup mypy for type checking
   - Timeline: Ongoing

---

## Contact & Questions

For questions about standardization, refer to:
- PYTHON_STYLE_GUIDE.md - For coding standards
- CODE_STANDARDIZATION_ANALYSIS.md - For refactoring analysis
- Docstrings in utility modules - For function usage

