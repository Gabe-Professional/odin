import argparse
from odin.collect.main import collect_main
from odin.groups import DateParent, TypeParent, QueryParent, ProjectParent


def setup_collect_parser(parser, parents=[]):
    p = parents.copy()

    date_specs = DateParent(group_title='Date Specification')
    elastic_specs = QueryParent(subtype='elastic', group_title='Elastic Query Options')
    postgres_specs = QueryParent(subtype='postgres', group_title='Postgres Query options')
    db_specs = TypeParent(subtype='database', group_title='Database Options')
    project_specs = ProjectParent(group_title='Project Specifications')

    p.extend([project_specs.parser, db_specs.parser, date_specs.parser, elastic_specs.parser, postgres_specs.parser])
    collect_parser = parser.add_parser('collect',
                                       description=collect_main.__doc__,
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       help='sub-command for collecting odin data',
                                       parents=p)

    # databases = collect_parser.add_argument_group('Database Options', 'Select the database to query')
    # databases.add_argument('--postgres', action='store_true', help='use this option to query postgres database')
    # databases.add_argument('--elastic', action='store_true', help='use this option to query elasticsearch database')
    #
    # project = collect_parser.add_argument_group('Project Options')
    # project.add_argument('-d', '--project_directory', help='the directory path to save your data.' , required=True)
    # project.add_argument('-sd', '--sub_dirs',
    #                      help='List of subdirectories you wish to create in you project directory',
    #                      nargs='*', default=None)
    #
    # gquery = collect_parser.add_argument_group('General Query Variables', 'Use these option for any available database')
    # gquery.add_argument('-st', '--start_time',
    #                     help='The start time for the period of data being exported. '
    #                          'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)')
    # gquery.add_argument('-et', '--end_time',
    #                     help='The end time for the period of data being exported. '
    #                          'Time must be in YYYY-MM-DDTHH:MM:SS.SSSZ format (ISO 8601)')
    #
    # gquery.add_argument('-c', '--cluster', choices=['DEV', 'PROD'], default='DEV',
    #                     help='which cluster of the database to query. the default  is DEV. '
    #                          ' for postgres, DEV is the only database available at this time')
    #
    # pquery = collect_parser.add_argument_group('Postgres Query Variables', 'Use these options for querying postgres')
    # pquery.add_argument('--min', action='store_true',
    #                     help='use this option while using the --postgres option to get messages in')
    # pquery.add_argument('--mout', action='store_true',
    #                     help='use this option while using the --postgres option to get messages in')
    #
    # equery = collect_parser.add_argument_group('Elasticsearch Query Variables',
    #                                            'Use these options for querying Elasticsearch')
    # equery.add_argument('-kw', '--keywords', nargs='*', default=None)
    # equery.add_argument('-dl', '--download', action='store_true',
    #                     help='using this option will download your elasticsearch data to your project directory.')

    collect_parser.set_defaults(func=collect_main)
