import argparse
from odin.collect.cli import setup_collect_parser
from odin.utils.cli import setup_project_parser
import logging
from importlib.metadata import version
import os
import sys
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
    # todo: need to make a better argument parser and subparsers...
    logging.info('Attempting to Load Subcommands')
    parser = subp.add_subparsers()
    setup_collect_parser(parser)
    setup_project_parser(parser)

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
start with `%(prog)s`.

USAGE
-----
    To Run this application and get help:
    $ %(prog)s -h

NOTES
-----
    The `%(prog)s` CLI has sub commands, each of which contain their own help information.  To
    figure out how to run a given command just keep using -h as you move down the tree until you
    have the full command flushed out.

----------------------------------------------------------------------------------------------

    """
    epilog = f"\n For more information on %(prog)s {version('odin')}, "
    epilog += "contact Gabe McBride <gabriel.mcbride@twosixtech.com>"
    main_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=run.__doc__,
                                          epilog=epilog)

    main_parser.add_argument("-v", "--verbose", action='count', default=0,
                             help="Logging Verbosity (Default: %(default)s")
    main_parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + version('odin'))
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


