import pytz
from tzlocal import get_localzone
from datetime import datetime, timedelta


class TimeZone:
    """Helper Class to define useful timezones"""
    utc = pytz.timezone("UTC")
    eastern = pytz.timezone('US/Eastern')
    central = pytz.timezone('US/Central')
    mountain = pytz.timezone('US/Mountain')
    pacific = pytz.timezone('US/Pacific')
    hawaii = pytz.timezone('US/Hawaii')
    alaska = pytz.timezone('US/Alaska')
    local = get_localzone()


def get_iso_datetime(dt, noSeparator=False):
    """Returns an ISO 8601 date/time string in UTC for a localized datetime.datetime.


    :param (datetime.datetime) dt:      A datetime object
    :param (bool) noSeparator:          Specify whether or not to use "-" and ":" in string
    :return (str):                      A String representing the time
    """
    if noSeparator is True:
        if dt.tzinfo == pytz.utc:
            return dt.strftime('%Y%m%dT%H%M%SZ')
        else:
            return dt.strftime('%Y%m%dT%H%M%S%z')
    else:
        if dt.tzinfo == pytz.utc:
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return dt.strftime('%Y-%m-%dT%H:%M:%S%z')


def DHMMS_string_to_timedelta(string):
    """Converts a  DD:HH:MM:SS duration string to a timedelta object.
    :param (str) string              DD:HH:MM:SS-formatted string
    return (datetime.timedelta)      timedelta reprsentation of string
    """
    multiplier = 1
    if string.startswith('-'):
        multiplier = -1

    def getDateTimeFromIso(iso):
        """Get a datetime.datetime object from ISO 8601 date/time string in UTC

        :param (str) iso:               A ISO 8601 Formatted date/time string
        :return (datetime.datetime):
        """

        pats = iter(['%Y%m%dT%H%M%S.%f%z', '%Y%m%dT%H%M%S%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z',
                     '%Y%m%d %H%M%S.%f%z', '%Y%m%d %H%M%S%z', '%Y-%m-%d %H:%M:%S.%f%z', '%Y-%m-%d %H:%M:%S%z'])

        for pat in pats:
            try:
                return TimeZone.utc.normalize(datetime.strptime(iso, pat))
            except ValueError:
                pass

        raise ValueError("{} is not in ISO format".format(iso))

    # Get rid of + or -
    string = string.strip('-').strip('+')

    my_times = string.split(':')
    if len(my_times)!=4:
        raise ValueError(f"{string} not formatted in DD:HH:MM:SS format.")

    my_times = list(map(int, my_times))

    return timedelta(days=my_times[0], hours=my_times[1], minutes=my_times[2], seconds=my_times[3]) * multiplier


def get_date_time_from_iso(iso):
    """Get a datetime.datetime object from ISO 8601 date/time string in UTC

    :param (str) iso:               A ISO 8601 Formatted date/time string
    :return (datetime.datetime):
    """

    pats = iter(['%Y%m%dT%H%M%S.%f%z', '%Y%m%dT%H%M%S%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z',
                 '%Y%m%d %H%M%S.%f%z', '%Y%m%d %H%M%S%z', '%Y-%m-%d %H:%M:%S.%f%z', '%Y-%m-%d %H:%M:%S%z'])

    for pat in pats:
        try:
            return TimeZone.utc.normalize(datetime.strptime(iso, pat))
        except ValueError:
            pass

    raise ValueError("{} is not in ISO format".format(iso))