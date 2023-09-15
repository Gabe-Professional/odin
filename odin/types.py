from odin.utils.time import TimeZone, get_date_time_from_iso, DHMMS_string_to_timedelta
import argparse
import os


def delta_argument(time_delta_string):
    """A type argument for when a value can be a date or a time delta.
    Resolves whether the string is an ISO string or a DD:HH:MM:SS string.

    :param time_delta_string (str)             ISO string or +/-DD:HH:MM:SS string
    :return delta (timedelta or datetime)      Either a timedelta or timedelta string.
    """

    if time_delta_string is None:
        return None

    try:
        return get_date_time_from_iso(time_delta_string)
    except ValueError:
        try:
            return DHMMS_string_to_timedelta(time_delta_string)
        except ValueError:
            msg = f"{time_delta_string} is not in ISO 8601 format or DD:HH:MM:SS format."
            raise argparse.ArgumentTypeError(msg)


def iso_argument(time_string):
    """Converts an ISO string to a UTC datetime.datetime object.
    :param time_string (str)                  ISO formatted string
    :return (datetime.datetime)               UTC datetime object
    """
    if time_string is None:
        return None

    try:
        return TimeZone.utc.normalize(get_date_time_from_iso(time_string))
    except ValueError:
        msg = "{} is not formatted in ISO 8601 format."
        raise argparse.ArgumentTypeError(msg)


def directory_argument(filePath):
    if os.path.exists(filePath) or os.access(filePath, os.W_OK):
        return filePath
    else:
        raise ValueError("{} is not a valid directory.".format(filePath))