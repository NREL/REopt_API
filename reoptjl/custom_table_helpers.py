# custom_table_helpers.py
from typing import Dict, Any, List, Union

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def clean_data_dict(data_dict: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    """Clean data dictionary by removing default values."""
    default_values = {0, float("nan"), "NaN", "0", "0.0", "$0.0", -0, "-0", "-0.0", "-$0.0", None}
    return {
        key: ["" if v in default_values else v for v in value_array]
        for key, value_array in data_dict.items()
    }

def sum_vectors(data: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any], Any]:
    """Sum numerical vectors within a nested data structure."""
    if isinstance(data, dict):
        return {key: sum_vectors(value) for key, value in data.items()}
    elif isinstance(data, list):
        return sum(data) if all(isinstance(item, (int, float)) for item in data) else [sum_vectors(item) for item in data]
    else:
        return data

def colnum_string(n: int) -> str:
    """Convert a column number to an Excel-style column string."""
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def safe_get(df: Dict[str, Any], key: str, default: Any = 0) -> Any:
    return df.get(key, default)