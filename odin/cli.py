import argparse
from odin.elastic_search import collect_main


def setup_parser():
    """A Commandline Interface (CLI) for working with Odin data
                """
    #### MAKE THE COMMANDLINE PARSER AND SUBPARSER ####

    parser = argparse.ArgumentParser(description='test description')
    parser.add_argument('--test')

    subparser = parser.add_subparsers(description='Functions of the Pyodin CLI')

    #### MAKE A SUBPARSER THAT COLLECTS DATA FROM ELASTIC SEARCH ####

    collect_parser = subparser.add_parser('collect')
    collect_parser.add_argument('--test')
    collect_parser.set_defaults(func=collect_main)
    #### PARSE THE ARGUMENTS ####
    args = parser.parse_args()

    args.func(args)


def run():
    setup_parser()

