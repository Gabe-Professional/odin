import argparse
from odin.collect.main import collect_main

def setup_parser():
    """
    A Commandline Interface (CLI) for working with Odin data with elastic search. \n\n

    test
    """
    # --------------------------------------------------------------------------------------------------------------- #
    #### MAKE THE COMMANDLINE PARSER AND SUBPARSER
    # --------------------------------------------------------------------------------------------------------------- #

    parser = argparse.ArgumentParser(description=setup_parser.__doc__)
    subparser = parser.add_subparsers(description=collect_main.__doc__)

    # --------------------------------------------------------------------------------------------------------------- #
    #### MAKE A SUBPARSER THAT COLLECTS DATA FROM ELASTIC SEARCH
    # --------------------------------------------------------------------------------------------------------------- #

    collect_parser = subparser.add_parser('collect')
    collect_parser.add_argument('--index_pattern', choices=['pulse-odin', 'pulse-odin*'], help='the correct odin index pattern to use')
    collect_parser.add_argument('--query_path', help='The filepath to the Elastic Search query. File should be in JSON format.')

    collect_parser.set_defaults(func=collect_main)

    # --------------------------------------------------------------------------------------------------------------- #
    #### ADD ANOTHER SUBPARSER HERE WHEN A NEW FUNCTION OF ODIN IS NEEDED
    # --------------------------------------------------------------------------------------------------------------- #
    #
    #
    #
    #
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

