# hourly_rate_helpers.py
from typing import Dict, Any, List
from datetime import datetime, timedelta
import calendar

def generate_datetime_column(year: int, time_steps_per_hour: int) -> List[str]:
    """
    Generate datetime strings for the first column based on year and time_steps_per_hour.
    
    Args:
        year: The year for the datetime series
        time_steps_per_hour: Number of time steps per hour (1, 2, or 4)
    
    Returns:
        List of datetime strings formatted as "M/D/YYYY H:MM"
    """
    # Check if leap year and adjust days accordingly
    is_leap = calendar.isleap(year)
    total_days = 365  # Always use 365 days, even for leap years
    
    # Calculate time step increment in minutes
    minutes_per_step = 60 // time_steps_per_hour
    
    datetime_list = []
    start_date = datetime(year, 1, 1, 0, 0)
    
    # Calculate total number of time steps
    total_steps = total_days * 24 * time_steps_per_hour
    
    for step in range(total_steps):
        current_time = start_date + timedelta(minutes=step * minutes_per_step)
        # Format: M/D/YYYY H:MM (Windows-compatible formatting)
        month = current_time.month
        day = current_time.day
        year = current_time.year
        hour = current_time.hour
        minute = current_time.minute
        formatted_time = f"{month}/{day}/{year} {hour}:{minute:02d}"
        datetime_list.append(formatted_time)
    
    return datetime_list


def get_monthly_peak_for_timestep(timestep_index: int, monthly_peaks: List[float], time_steps_per_hour: int) -> float:
    """
    Get the monthly peak value for a given timestep index.
    
    Args:
        timestep_index: The index of the current timestep
        monthly_peaks: List of 12 monthly peak values
        time_steps_per_hour: Number of time steps per hour
    
    Returns:
        The monthly peak value for the month containing this timestep
    """
    # Calculate which month this timestep belongs to
    # Approximate days per month
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    steps_per_day = 24 * time_steps_per_hour
    cumulative_steps = 0
    
    for month_idx, days in enumerate(days_in_months):
        cumulative_steps += days * steps_per_day
        if timestep_index < cumulative_steps:
            return monthly_peaks[month_idx] if month_idx < len(monthly_peaks) else 0
    
    # Default to last month if we're beyond December
    return monthly_peaks[-1] if monthly_peaks else 0


def safe_get_list(data: Dict[str, Any], key: str, default: List = None) -> List:
    """
    Safely get a list value from nested dictionary.
    
    Args:
        data: The dictionary to search
        key: Dot-separated key path (e.g., "outputs.ElectricLoad.load_series_kw")
        default: Default value if key not found
    
    Returns:
        The found list or default value
    """
    if default is None:
        default = []
    
    keys = key.split('.')
    current = data
    
    try:
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k)
            else:
                return default
            
            if current is None:
                return default
        
        return current if isinstance(current, list) else default
    except (KeyError, TypeError, AttributeError):
        return default


def safe_get_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from nested dictionary.
    
    Args:
        data: The dictionary to search
        key: Dot-separated key path
        default: Default value if key not found
    
    Returns:
        The found value or default
    """
    keys = key.split('.')
    current = data
    
    try:
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k)
            else:
                return default
            
            if current is None:
                return default
        
        return current
    except (KeyError, TypeError, AttributeError):
        return default
