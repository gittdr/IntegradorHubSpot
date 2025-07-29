from datetime import datetime

def safe_int(value):
    """
    Safely convert a value to an integer, returning 0 if conversion fails.
    :param value: The value to convert.
    :return: The converted integer or 0 if conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        # print(f"Error converting {value} to int, returning 0")
        return 0

def safe_float(value):
    """
    Safely convert a value to a float, returning 0.0 if conversion fails.
    :param value: The value to convert.
    :return: The converted float or 0.0 if conversion fails.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_datetime(value):
    """
    Safely convert a value to a datetime object, returning None if conversion fails.
    :param value: The value to convert.
    :return: The converted datetime object or None if conversion fails.
    """
    try:
        if not value:
            return None
        date = datetime.fromisoformat(value.replace("Z", ""))
        date_sql = date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return date_sql
    except (ValueError, TypeError):
        return None