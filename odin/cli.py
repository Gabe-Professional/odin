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

    collect_parser = subparser.add_parser('collect', description=collect_main.__doc__)
    collect_parser.add_argument('--index_pattern', choices=['pulse-odin', 'pulse-odin*'], help='the correct odin index pattern to use.')
    collect_parser.add_argument('--query_path', help='The filepath to the Elastic Search query. File should be in JSON format.')
    collect_parser.add_argument('--start_time', help='The start time for the period of data being exported. '
                                                     'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)')
    collect_parser.add_argument('--end_time', help='The end time for the period of data being exported.'
                                                   'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)')
    # todo: need to add a function for custom attributes...or different groups based on the task...
    #  task informs data fields

    collect_parser.set_defaults(func=collect_main)

    # --------------------------------------------------------------------------------------------------------------- #
    #### MAKE A SUBPARSER THAT ANALYZES ODIN DATASETS
    # --------------------------------------------------------------------------------------------------------------- #

    analyze_parser = subparser.add_parser('analyze', description=analyze_main.__doc__)
    analyze_parser.add_argument('--method', choices=['kmeans'])
    analyze_parser.add_argument('--file_path', help='path to the odin csv dataset')

    analyze_parser.set_defaults(func=analyze_main)

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

