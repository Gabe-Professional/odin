import argparse
from odin.collect.main import collect_main


def setup_collect_parser(parser):
    collect_parser = parser.add_parser('collect',
                                       description=collect_main.__doc__,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    collect_parser.add_argument("-v", "--verbose", action='count', default=0,
                                help="Logging Verbosity (Default: %(default)s")

    collect_parser.add_argument('-d', '--project_directory', help='the directory path to save your data.',
                                required=True)
    collect_parser.add_argument('-sd', '--sub_dirs',
                                help='List of subdirectories you wish to create in you project directory',
                                nargs='*', default=None)

    collect_parser.add_argument('-st', '--start_time',
                                help='The start time for the period of data being exported. '
                                     'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)',
                                required=True)

    collect_parser.add_argument('-et', '--end_time',
                                help='The end time for the period of data being exported. '
                                     'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)',
                                required=True)

    collect_parser.add_argument('-db', '--database',
                                choices=['postgres', 'elastic'],
                                help='The database object you wish to query',
                                required=True)

    collect_parser.add_argument('-c', '--cluster',
                                choices=['DEV', 'PROD'],
                                default='DEV')
    collect_parser.add_argument('-md', '--message_direction',
                                choices=['in', 'out'],
                                default='in')

    collect_parser.add_argument('-kw', '--keywords', nargs='*', default=None,
                                help='Add keywords to your elasticsearch query')
    collect_parser.add_argument('-dl', '--download', choices=[True, False], default=True,
                                help='Add boolean argument to download the data to your project directory')

    collect_parser.set_defaults(func=collect_main)
