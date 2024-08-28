# custom table helpers.py
def flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def clean_data_dict(data_dict):
    """Clean data dictionary by removing default values."""
    for key, value_array in data_dict.items():
        new_value_array = [
            "" if v in [0, float("nan"), "NaN", "0", "0.0", "$0.0", -0, "-0", "-0.0", "-$0.0", None] else v
            for v in value_array
        ]
        data_dict[key] = new_value_array
    return data_dict

def sum_vectors(data):
    """Sum numerical vectors within a nested data structure."""
    if isinstance(data, dict):
        return {key: sum_vectors(value) for key, value in data.items()}
    elif isinstance(data, list):
        if all(isinstance(item, (int, float)) for item in data):
            return sum(data)
        else:
            return [sum_vectors(item) for item in data]
    else:
        return data

def colnum_string(n):
    """Convert a column number to an Excel-style column string."""
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def safe_get(df, key, default=0):
    return df.get(key, default)

def check_bau_consistency(scenarios, tolerance_percentage=0.1):
    """
    Check the consistency of BAU values within the 'outputs.Financial' section across all scenarios with a percentage-based tolerance.

    Args:
        scenarios (list): List of scenario dictionaries to check.
        tolerance_percentage (float): Tolerance percentage for allowable differences.
                                      For example, 0.1 for 0.1% tolerance.
    """
    bau_values_list = []
    all_bau_keys = set()

    for scenario in scenarios:
        df_gen = flatten_dict(scenario['full_data'])

        current_bau_values = {}
        for key, value in df_gen.items():
            # Focus only on keys related to 'outputs.Financial' and ending with '_bau'
            if key.startswith('outputs.Financial') and key.endswith('_bau'):
                current_bau_values[key] = value
                all_bau_keys.add(key)

        bau_values_list.append(current_bau_values)

    # Perform consistency check across all `_bau` values within 'outputs.Financial'
    first_bau_values = bau_values_list[0]
    for idx, other_bau_values in enumerate(bau_values_list[1:], start=1):
        for key in all_bau_keys:
            first_value = first_bau_values.get(key, 0)
            other_value = other_bau_values.get(key, 0)
            if first_value != 0:  # Avoid division by zero
                difference = abs(first_value - other_value)
                tolerance = abs(first_value) * (tolerance_percentage / 100)
                if difference > tolerance:
                    raise ValueError(f"Inconsistent BAU values found between scenario 1 and scenario {idx + 1}. Please check the BAU values for consistency.")
            else:  # Handle the case where the first value is 0
                if abs(other_value) > tolerance:
                    raise ValueError(f"Inconsistent BAU values found between scenario 1 and scenario {idx + 1}. Please check the BAU values for consistency.")
