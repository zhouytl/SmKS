# Python Code Style Guide and Best Practices

**SmKS Project - Code Standardization Guidelines**  
**Created:** April 26, 2026

---

## Table of Contents
1. [File Structure](#file-structure)
2. [Naming Conventions](#naming-conventions)
3. [Documentation](#documentation)
4. [Imports](#imports)
5. [Code Formatting](#code-formatting)
6. [Functions](#functions)
7. [Error Handling](#error-handling)
8. [Comments](#comments)
9. [Module Organization](#module-organization)

---

## File Structure

### Standard File Header
Every Python file should start with:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[One-line module description]

[Detailed description of what this module does, its purpose, and main functionality]

Created on [DATE]
@author: zhouyangtianli
"""
```

### Example:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization utilities for seismic data plotting.

This module provides functions for creating publication-quality plots
of seismic waveforms, event locations, and analysis results.

Created on April 26, 2026
@author: zhouyangtianli
"""
```

---

## Naming Conventions

### Functions and Variables
- Use **snake_case** for function and variable names
- ✅ Good: `cal_raypath()`, `plot_data_matrix()`, `sample_rate`
- ❌ Bad: `calcRaypath()`, `plotDataMatrix()`, `SampleRate`

### Constants
- Use **UPPER_CASE** for module-level constants
- ✅ Good: `DEFAULT_SAMPLE_RATE = 100.0`, `CMB_DEPTH = 2891`
- ❌ Bad: `default_sample_rate = 100.0`

### Classes
- Use **PascalCase** for class names
- ✅ Good: `SeismicData`, `RayPathCalculator`

### Private Functions/Variables
- Prefix with underscore for internal use only
- ✅ Good: `_internal_helper()`, `_temp_variable`

### Boolean Variables
- Use `is_`, `has_`, `can_`, `should_` prefixes
- ✅ Good: `is_valid`, `has_data`, `can_plot`, `should_skip`

---

## Documentation

### Function Docstrings (Google Style)

Every function MUST have a docstring. Use the following format:

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great circle distance between two points.
    
    Uses the Haversine formula to compute the shortest distance
    between two points on Earth's surface.
    
    Args:
        lat1 (float): Latitude of first point in degrees
        lon1 (float): Longitude of first point in degrees
        lat2 (float): Latitude of second point in degrees
        lon2 (float): Longitude of second point in degrees
        
    Returns:
        float: Distance in kilometers
        
    Raises:
        ValueError: If coordinates are outside valid ranges
        
    Example:
        >>> distance = calculate_distance(40.7128, -74.0060, 51.5074, -0.1278)
        >>> print(distance)
        5570.2
        
    Note:
        This assumes a spherical Earth model. For higher accuracy,
        use an ellipsoid model.
    """
    # Implementation here
    pass
```

### Docstring Components

1. **Summary Line** (one line)
   - Brief, imperative description
   - ✅ Good: "Calculate great circle distance between points"
   - ❌ Bad: "This function calculates distance"

2. **Extended Description** (optional)
   - Detailed explanation of behavior
   - Additional context or limitations

3. **Args**
   - List all parameters
   - Include type and description for each
   - Use (type) notation

4. **Returns**
   - Describe return value(s)
   - Include type information

5. **Raises**
   - List possible exceptions
   - Explain when they occur

6. **Example**
   - Provide usage examples
   - Should be runnable code

7. **Note** (optional)
   - Important caveats or assumptions

---

## Imports

### Organization Order
Imports should be organized in this order, separated by blank lines:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module docstring"""

# Standard library imports
import os
import sys
from pathlib import Path
from glob import glob
from datetime import datetime

# Third-party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import scipy.signal

# Obspy imports
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
from obspy.signal.rotate import rotate2zne

# Cartopy imports
from cartopy import crs as ccrs
import cartopy.feature as cfeature

# Local imports
from raypath_utils import cal_raypath, cal_pierce
from visualization_utils import plot_data_matrix
```

### Import Guidelines
- ✅ Use specific imports: `from module import function`
- ❌ Avoid wildcard imports: `from module import *`
- ✅ Group imports by type (stdlib, third-party, local)
- ✅ Sort alphabetically within groups
- ❌ Never scatter imports throughout the file

---

## Code Formatting

### Line Length
- Maximum 100 characters per line
- Use line continuation for long expressions

```python
# ✅ Good: Line continuation
long_variable = (very_long_expression_part_1 +
                 very_long_expression_part_2 +
                 very_long_expression_part_3)

# ❌ Bad: Too long
long_variable = very_long_expression_part_1 + very_long_expression_part_2 + very_long_expression_part_3
```

### Indentation
- Use 4 spaces (not tabs)
- Consistent indentation across all files

### Blank Lines
- 2 blank lines between top-level functions/classes
- 1 blank line between methods in a class
- Use blank lines to separate logical sections within functions

```python
def function1():
    """First function"""
    pass


def function2():
    """Second function with sections"""
    
    # Section 1: Data preparation
    data = prepare_data()
    
    # Section 2: Processing
    result = process(data)
    
    return result
```

### Spacing
- Use spaces around operators: `a = b + c` not `a=b+c`
- No space after function name in definition: `def func(x):` not `def func (x):`
- No extra spaces in lists: `[1, 2, 3]` not `[1, 2, 3 ]`

---

## Functions

### Function Guidelines

1. **Keep functions small and focused**
   - One primary responsibility
   - Ideally < 50 lines
   - If > 100 lines, consider breaking up

2. **Parameters**
   - Limit to 5-7 parameters
   - Use positional for required args
   - Use keyword arguments with defaults for optional args
   - Group related parameters

3. **Return Values**
   - Return early on error conditions
   - Return single value or tuple, avoid mixed types
   - Be consistent in return types

### Example of Well-Structured Function

```python
def process_seismic_data(data_file, sample_rate=100.0, 
                         lowpass_freq=1.0, 
                         output_dir=None):
    """
    Load and process seismic waveform data.
    
    Reads SAC format seismic data, applies filtering, and optionally
    saves results to disk.
    
    Args:
        data_file (str): Path to input SAC file
        sample_rate (float): Target sampling rate in Hz (default: 100.0)
        lowpass_freq (float): Lowpass filter frequency in Hz (default: 1.0)
        output_dir (str, optional): Directory for output files
        
    Returns:
        np.ndarray: Processed waveform data
        
    Raises:
        FileNotFoundError: If data_file doesn't exist
        ValueError: If sample_rate or lowpass_freq are invalid
    """
    # Input validation
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"File not found: {data_file}")
    
    if sample_rate <= 0:
        raise ValueError(f"Invalid sample_rate: {sample_rate}")
    
    # Load data
    stream = read(data_file)
    trace = stream[0]
    
    # Process
    trace.resample(sample_rate)
    trace.filter('lowpass', freq=lowpass_freq)
    
    # Output
    result = trace.data
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        np.save(f'{output_dir}/processed.npy', result)
    
    return result
```

---

## Error Handling

### Exception Handling

```python
# ✅ Good: Specific exceptions
try:
    value = int(user_input)
except ValueError:
    print("Please enter a valid integer")
except KeyboardInterrupt:
    print("Operation cancelled")

# ❌ Bad: Catching all exceptions
try:
    value = int(user_input)
except:
    print("Something went wrong")
```

### Raising Exceptions

```python
# ✅ Good: Specific, informative
if not data:
    raise ValueError("Data cannot be empty")

if index < 0 or index >= len(data):
    raise IndexError(f"Index {index} out of range [0, {len(data)-1}]")

# ❌ Bad: Vague
if not data:
    raise Exception("Error")
```

---

## Comments

### Comment Guidelines

1. **Use comments to explain WHY, not WHAT**
   
   ```python
   # ✅ Good: Explains reasoning
   # Use quadratic interpolation to improve accuracy near peaks
   peak_value = quadratic_interpolate(data[i-1:i+2])
   
   # ❌ Bad: Obvious from code
   # Set peak_value
   peak_value = data[i]
   ```

2. **Keep code self-documenting**
   - Use clear variable names
   - Use clear function names
   - Avoid cryptic abbreviations

3. **Update comments when code changes**
   - Stale comments are worse than no comments
   - Comments should reflect current behavior

4. **Inline comments**
   ```python
   # Good: Separate explanation from code
   x = x + 1  # Increment counter
   
   # Bad: Confusing placement
   x = x + 1  # x  # counter
   ```

---

## Module Organization

### Typical File Organization

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module docstring"""

# === IMPORTS ===
import numpy as np
import pandas as pd
from .utils import helper_function

# === CONSTANTS ===
DEFAULT_SAMPLE_RATE = 100.0
CMB_DEPTH = 2891  # km

# === GLOBAL OBJECTS ===
_model_prem = None  # Lazy-loaded PREM model


# === UTILITY FUNCTIONS ===
def _internal_helper():
    """Private helper function."""
    pass


def public_function1(param1, param2):
    """Public function 1."""
    pass


def public_function2(param1):
    """Public function 2."""
    pass


# === MAIN EXECUTION ===
if __name__ == "__main__":
    # Example usage or tests
    result = public_function1(1, 2)
    print(result)
```

---

## Project-Specific Utilities

### Available Utility Modules

1. **raypath_utils.py**
   - `cal_raypath()` - Calculate great circle raypaths
   - `cal_pierce()` - Calculate CMB piercing points
   - `cal_pierce_and_bounce()` - Calculate multiple bounce points

2. **visualization_utils.py** *(NEW)*
   - `plot_data_matrix()` - Plot seismic waveforms
   - `plot_eq_map()` - Plot epicenter and stations
   - `hex_to_kml_color()` - Convert hex colors to KML format

3. **data_utils.py** *(NEW)*
   - `cal_dist_time()` - Calculate distances and arrival times
   - `traces_to_matrix()` - Convert SAC files to matrix
   - `matrix_align_slant()` - Align seismic traces

---

## Checklist for New Code

Before submitting code, check:

- [ ] File starts with proper header (shebang, encoding, docstring)
- [ ] Imports organized and in alphabetical order
- [ ] All functions have docstrings
- [ ] Function names use snake_case
- [ ] Constants use UPPER_CASE
- [ ] Line length < 100 characters
- [ ] No wildcard imports
- [ ] Comments explain WHY, not WHAT
- [ ] No debug print() statements left
- [ ] Error handling with specific exceptions
- [ ] Code runs without warnings
- [ ] Related functions in appropriate utility module

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-26 | Initial standardization guide |

---

## Questions?

Refer to this guide first, then consult the CODE_STANDARDIZATION_ANALYSIS.md file for project-specific recommendations.

