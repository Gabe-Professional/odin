import argparse
import sre_parse

import pkg_resources

from odin.collect.main import collect_main
from odin.analyze.main import analyze_main
import logging
logger = logging.getLogger(__name__)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ValidationException(Exception):
    pass

def pass_message(msg):
    return "{}".format(msg)+"."*5+"{}PASSED{}".format(bcolors.OKGREEN,bcolors.ENDC)


def fail_message(msg):
    return "{}".format(msg)+"."*5+"{}FAILED{}".format(bcolors.FAIL,bcolors.ENDC)


def warn_message(msg):
    return "{}".format(msg)+"."*5+"{}WARNING{}".format(bcolors.WARNING,bcolors.ENDC)


def error_message(msg):
    return "{}".format(msg)+"."*5+"{}{}ERROR{}".format(bcolors.UNDERLINE, bcolors.FAIL, bcolors.ENDC)


def setup_parser(subp):
    logging.info('Attempting to Load Subcommands')
    parser = subp.add_subparsers()
    collect_parser = parser.add_parser('collect',
                                       description=collect_main.__doc__,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    collect_parser.add_argument("-v", "--verbose", action='count', default=0,
                                help="Logging Verbosity (Default: %(default)s")

    collect_parser.add_argument('-d', '--project_directory', help='the directory path to save your data.',
                                required=True)
    collect_parser.add_argument('-sd', '--sub_directories',
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
                                choices=['postgres'],
                                help='The database object you wish to query',
                                required=True)

    collect_parser.add_argument('-c', '--cluster',
                                choices=['DEV'],
                                default='DEV')
    collect_parser.add_argument('-md', '--message_direction',
                                choices=['in', 'out'],
                                default='in')

    collect_parser.add_argument('--pretty_data',
                                choices=[True, False],
                                default=False,
                                help='Add this optional argument to make the data into a pretty dataframe. '
                                     'Default option for this argument is False')

    collect_parser.set_defaults(func=collect_main)
    args = subp.parse_args()
    if args.verbose == 0:
        logging.getLogger().setLevel(logging.WARNING)
        logging.warning('Setting log level to: WARNING')
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
        logging.info('Setting log level to: INFO')
    elif args.verbose >= 2:

        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Setting Log Level to: DEBUG")

    args.func(args)


def run():
    """ODIN Command Line Interface (CLI) Application
----------------------------------------------------------------------------------------------
This is the main entrypoint into the odin CLI applications. Note all odin cli will
start with `odin`.

USAGE
-----
    To Run this application and get help:
    $ odin -h

NOTES
-----
    The `odin` CLI has sub commands, each of which contain their own help information.  To
    figure out how to run a given command just keep using -h as you move down the tree until you
    have the full command flushed out.

----------------------------------------------------------------------------------------------

    """
    epilog = "\n For more information, "
    epilog += "contact Gabe McBride <gabriel.mcbride@twosixtech.com>"
    main_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=run.__doc__,
                                          epilog=epilog)

    main_parser.add_argument("-v", "--verbose", action='count', default=0,
                             help="Logging Verbosity (Default: %(default)s")
    # SET LOGGING
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s--%(name)s:%(levelname)s:--%(message)s')
    logging.getLogger().setLevel(logging.INFO)

    # todo: test out parents argument
    try:
        setup_parser(main_parser)
    except ValidationException as e:
        logging.error(e)
    except Exception as e:
        logging.exception(e)


