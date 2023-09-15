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

    collect_parser.set_defaults(func=collect_main)
