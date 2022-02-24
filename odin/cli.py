import argparse
from odin.collect.main import collect_main
import logging


def setup_parser():
    """A Commandline Interface (CLI) for working with Odin data
                """
    #### MAKE THE COMMANDLINE PARSER AND SUBPARSER ####

    parser = argparse.ArgumentParser(description='test description')
    subparser = parser.add_subparsers(description='Functions of the Odin CLI')

    #### MAKE A SUBPARSER THAT COLLECTS DATA FROM ELASTIC SEARCH ####

    collect_parser = subparser.add_parser('collect')
    collect_parser.add_argument('--es_cred_file')

    collect_parser.set_defaults(func=collect_main)
    #### PARSE THE ARGUMENTS ####
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

