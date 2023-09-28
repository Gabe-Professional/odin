import argparse
import os
from .types import iso_argument, delta_argument, directory_argument
from odin.utils.time import TimeZone, get_iso_datetime
from datetime import datetime, timedelta
import sys as _sys


class SortContacts(argparse.Action):

    def __call__(self, parser, namespace, value, option_strings=None):
        """Given a list of values, sorts them into uuid and non-uuid destinations."""

        contacts = []
        if value is None:
            setattr(namespace, self.dest, None)

        else:
            for v in value:
                contacts.append(v)
            setattr(namespace, self.dest, sorted(contacts))


class ISOHelpAction(argparse.Action):
    """This is a custom argparse action that prints a help message on iso time."""

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help="more info on ISO8601"):
        super(ISOHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        about_iso = """
        Odin uses the international standard ISO8601 to represent dates and times. In ISO8601, a combined 
        date time is represented as:

                            YYYY-MM-DDThh:mm:ss.fff+/-00:00

        Broken into its components:

        YYYY: 
            the 4-digit year
        MM: 
            the 2-digit month (01 through 12)
        DD: 
            the 2-digit day (01 through 31)
        T: 
            an indicator that the time is about to be written ('T' is always just T).
        hh: 
            the zero-padded hour between 00 and 24. 24 is midnight.
        mm: 
            the zero-padded minute
        ss: 
            the zero-padded second
        .fff: 
            any miliseconds. Optional.
        +/-00:00 
            The timezone delta from UTC time. Can be replaced with just "Z" if the timezone is UTC. Timezone is 
            obligatory.

        Your clock's present ISO8601 time is {}
        
        """.format(get_iso_datetime(datetime.now(TimeZone.local)))


        formatter = parser._get_formatter()
        formatter.add_text(about_iso)
        parser._print_message(formatter.format_help(), _sys.stdout)
        parser.exit()


class TimePeriod(argparse.Action):
    """A class to assemble a time period, conducting post-processing on namespace.end if needed. Only for setting
    namespace.stop (since that can come in as a timedelta.

    Note: in order to properly reconcile variables, if you set one value with a datetime you have to set the other now.
    Otherwise the action doesn't know when to check to make sure start isn't later than stop. If you set a timedelta
    and leave the default value in place, that's fine - it doesn't need to check namespace.start <= namespace.stop
    in that case.
    """

    def __init__(self, option_strings, *args, **kwargs):
        super(TimePeriod, self).__init__(option_strings=option_strings,
                                         *args, **kwargs)

    def __call__(self, parser, namespace, value, option_strings=None):
        if (self.dest != 'stop') and (self.dest != 'start'):
            raise ValueError("This action is only for setting stop and start.")

        # if it doesn't have a default, argument is required.
        for action in parser._actions:
            if (action.dest == 'start') or (action.dest == 'stop'):
                if action.default is None:
                    action.required = True

        if isinstance(value, datetime):
            # This start and stop now required - time defaults are only valid if they're both left alone, or you're only
            # setting a timedelta via stop. Otherwise you can't reconcile the times and make sure they're valid.
            for action in parser._actions:
                if (action.dest == 'start') or (action.dest == 'stop'):
                    setattr(action, 'required', True)

        # Set the fed value
        setattr(self, self.dest, value)

        if self.dest == 'stop':
            if isinstance(value, timedelta):
                st = None
                # Try to get the set start tijme.
                for action in parser._actions:
                    if action.dest == 'start':
                        if hasattr(action, 'start'):
                            st = getattr(action, 'start')
                # Otherwise, use the default (already in the namespace. If it's valid (not none), use it to set values.
                st = getattr(namespace, 'start')
                if st is not None:
                    # If less than zero, stop is set in start, and start in stop.
                    if value.total_seconds() < 0:
                        setattr(namespace, 'start', st + value)
                        setattr(namespace, 'stop', st)

                    # Else, just set it normally.
                    else:
                        setattr(namespace, 'stop', st + value)
                else:
                    pass

            else:
                start_set = False
                # check if start has been set.
                for action in parser._actions:
                    if action.dest == 'start':
                        if hasattr(action, 'start'):
                            start_set = True

                setattr(namespace, self.dest, value)

                # If it has, make sure the times reconcile.
                if start_set is True:
                    if namespace.start >= namespace.stop:
                        parser.error("Time start {} cannot be greater or equal to time stop {}.".format(namespace.start,
                                                                                                        namespace.stop))

        # Now looking at the start case.
        else:
            stop_set = False
            stop_value = None
            for action in parser._actions:
                if action.dest == 'stop':
                    if hasattr(action, 'stop'):
                        stop_set = True
                        stop_value = getattr(action, action.dest)
            # If stop was a timedelta, do some math.
            if isinstance(stop_value, timedelta):
                set_stop_value = stop_value + value
                # Switch start and stop if negative timedelta
                if stop_value.total_seconds() < 0 :
                    setattr(namespace, 'start', set_stop_value)
                    setattr(namespace, 'stop', value)
                else:
                    setattr(namespace, 'start', value)
                    setattr(namespace, 'stop', set_stop_value)
            else:
                setattr(namespace, 'start', value)
                if stop_set is True:
                    if namespace.start >= namespace.stop:
                        parser.error("Time start {} cannot be greater or equal to time stop {}.".format(namespace.start,
                                                                                                        namespace.stop))


class BaseParent(object):
    """A class for creating unique instances of cli parents. Without this, attempting to customize a parent will apply
    changes across all instances of the parent (example: trying to switch argument defaults)."""
    default_title = ''

    def __init__(self, parser=None, group_title=None):

        if parser is None:
            self.parser = argparse.ArgumentParser(add_help=False)
        else:
            self.parser = parser

        if group_title is None:
            self.title = self.default_title
        else:
            self.title = group_title

        self.group = self.parser.add_argument_group(title=self.title)

        self._add_arguments()

    def _add_arguments(self):
        raise NotImplementedError("Implemented by classes that inherit.")


# Date Parent group

class DateParent(BaseParent):
    default_title = 'Time Window Specification'

    def __init__(self, parser=None, group_title=None):

        super(DateParent, self).__init__(parser, group_title)

    def _add_arguments(self):
        self.group.add_argument('--start', '-a',
                                action=TimePeriod,
                                type=iso_argument,
                                help='The start time for the period of data being queried. '
                                     'Start time in ISO 8601 format.')

        self.group.add_argument('--stop', '--delta', '-b',
                                action=TimePeriod,
                                type=delta_argument,
                                help='The end time for the period of data being queried. '
                                     'The ISO 8601 end time DD:HH:MM:SS.SSSZ.')
        # self.group.add_argument('--last7', help='quick query for the last seven days of data.')

        self.group.add_argument('--iso_help', help='More info on ISO8601.', action=ISOHelpAction)


class TypeParent(BaseParent):

    default_title = 'Database Specification'

    def __init__(self, parser=None, group_title=None, subtype=None):

        _type = ['database', 'api', None]
        if subtype not in _type:
            raise ValueError(f'Not a valid subtype. please choose from {", ".join(_type)}')
        self.subtype = subtype
        super(TypeParent, self).__init__(parser, group_title)

    def _add_arguments(self):

        if self.subtype == 'database':

            self.group.add_argument('--elastic', action='store_true',
                                    help='use this option to query elasticsearch database')
            self.group.add_argument('--postgres', action='store_true', help='use this option to query postgres database')

            self.group.add_argument('--cluster', '-c', choices=["DEV", "PROD"], default="DEV",
                                    help="The cluster from which to pull the data.")

        elif self.subtype in ['api']:
            raise NotImplementedError('Coming soon.')


# todo: make a new class or combine with query parent?
class QueryParent(BaseParent):
    default_title = 'Time Window Specification'

    def __init__(self, parser=None, group_title=None, subtype=None):
        databases = ['elastic', 'postgres', None]
        if subtype not in databases:
            raise ValueError(f'Not a valid subtype. please choose from {", ".join(databases)}')
        self.subtype = subtype

        super(QueryParent, self).__init__(parser, group_title)

    def _add_arguments(self):

        if self.subtype in ['elastic']:
            self.group.add_argument('--keywords', '-kw', nargs='*', default=None)
            self.group.add_argument('--download', '-dl', action='store_true', help='option for saving your data from elasticsearch')
        elif self.subtype in ['postgres']:
            self.group.add_argument('--message_in', '-i', action='store_true')
            self.group.add_argument('--message_out', '-o', action='store_true')
            self.group.add_argument('--contact_id', '--CID', dest='contact', nargs='+', action=SortContacts)


class ProjectParent(BaseParent):
    default_title = 'Time Window Specification'

    def __init__(self, parser=None, group_title=None):

        super(ProjectParent, self).__init__(parser, group_title)

    def _add_arguments(self):

        self.group.add_argument('--project_dir', '-d', type=directory_argument, default=os.getcwd())
        self.group.add_argument('--sub_dirs', '-sd', nargs='*', default=None)
