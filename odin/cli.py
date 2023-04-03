import argparse
from odin.collect.main import collect_main
from odin.analyze.main import analyze_main

def setup_parser():
    """
    A Commandline Interface (CLI) for working with Odin data with elastic search. \n\n

    test
    """
    # --------------------------------------------------------------------------------------------------------------- #
    #### MAKE THE COMMANDLINE PARSER AND SUBPARSER
    # --------------------------------------------------------------------------------------------------------------- #

    parser = argparse.ArgumentParser(description=setup_parser.__doc__)
    subparser = parser.add_subparsers(description='Sub-functions of the odin program')

    # --------------------------------------------------------------------------------------------------------------- #
    #### MAKE A SUBPARSER THAT COLLECTS DATA FROM ELASTIC SEARCH
    # --------------------------------------------------------------------------------------------------------------- #

    collect_parser = subparser.add_parser('collect',
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=collect_main.__doc__)
    collect_parser.add_argument('--project_directory', help='the directory path to save your data.',
                                required=True)
    collect_parser.add_argument('--sub_directories', help='List of subdirectories you wish to create in you project'
                                                          'directory', nargs='*', default=None)

    collect_parser.add_argument('--start_time', help='The start time for the period of data being exported. '
                                                     'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)',
                                required=True)
    collect_parser.add_argument('--end_time', help='The end time for the period of data being exported. '
                                                   'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)',
                                required=True)
    collect_parser.add_argument('--database', choices=['postgres'], help='The database object you wish to query',
                                required=True)
    collect_parser.add_argument('--cluster', choices=['DEV'], default='DEV')
    collect_parser.add_argument('--message_direction', choices=['in', 'out'], default='in')

    # todo: add summarize function as positional arg?
    # todo: add save function as argument to save summary...maybe save messages as well.

    collect_parser.set_defaults(func=collect_main)

    # --------------------------------------------------------------------------------------------------------------- #
    #### MAKE A SUBPARSER THAT ANALYZES ODIN DATASETS
    # --------------------------------------------------------------------------------------------------------------- #

    # analyze_parser = subparser.add_parser('analyze', description=analyze_main.__doc__)
    # analyze_parser.add_argument('--method', choices=['kmeans'])
    # analyze_parser.add_argument('--file_path', help='path to the odin csv dataset')
    #
    # analyze_parser.set_defaults(func=analyze_main)

    # --------------------------------------------------------------------------------------------------------------- #
    #### PARSE THE ARGUMENTS
    # --------------------------------------------------------------------------------------------------------------- #

    args = parser.parse_args()

    # todo: need to figure out verbose parser and what it is used for...
    # if args.verbose == 0:
    #
    #     logging.getLogger().setLevel(logging.WARNING)
    #     logging.warning("Setting Log Level to: WARNING")
    # elif args.verbose == 1:
    #     logging.getLogger().setLevel(logging.INFO)
    #     logging.info("Setting Log Level to: INFO")
    # elif args.verbose >= 2:
    #
    #     logging.getLogger().setLevel(logging.DEBUG)
    #     logging.debug("Setting Log Level to: DEBUG")

    args.func(args)


def run():
    setup_parser()

