# custom table helpers.py
def get_with_suffix(df, key, suffix, default_val=0):
    """Fetch value from dataframe with an optional retriaval of _bau suffix."""
    if not key.endswith("_bau"):
        key = f"{key}{suffix}"
    return df.get(key, default_val)

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
