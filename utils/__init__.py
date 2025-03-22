from datetime import datetime, timezone

def datetime_string(filename=False):
    """
    Creates ISO timestamp from current UTC time

    Args:
        filename (bool): Whether the timestamp is for a filename or not.
                        If true, changes time dividers from : to -
    Returns:
        str: Current UTC time as ISO timestamp
    """

    now = datetime.now(timezone.utc)
    if filename:
        return now.strftime("%Y-%m-%dT%H-%M-%SZ")
    else:
        return now.strftime("%Y-%m-%dT%H:%M:%SZ")