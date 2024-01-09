from datetime import datetime, timedelta
import pandas as pd
from odin.collect.postgres import Db


def get_date(date_time):
    date_string = pd.to_datetime(str(date_time).split(' ')[0]).date()
    return date_string


def get_platform(urn: str):
    if 'telegram' in urn:
        return 'telegram'
    elif 'whatsapp' in urn:
        return 'whatsapp'
    elif len(urn.split('-')) == 5:
        return 'engage'
    else:
        return None


def main(arguments):

    # GET THE INPUTS FOR QUERYING
    start = arguments.start
    stop = arguments.stop
    if arguments.start is None and arguments.stop is None:
        start = datetime.now().date()
        stop = start + timedelta(days=-30)

    # QUERY THE DATA
    with Db.Create('DEV') as pg:
        data = pg.get_contacts_by_datetime(start, stop)

    # MAKE SOME DATA
    data['date'] = data['created_datetime'].apply(lambda x: get_date(x))
    data['platform'] = data['contact_urn'].apply(lambda x: get_platform(x))

    summary = data.groupby(['date', 'platform']).contact_id.count().unstack().reset_index().fillna(value=0)


    print(summary)


if __name__ == '__main__':
    import argparse
    import odin.groups as gps

    verbose_parser = argparse.ArgumentParser(add_help=False)
    verbose_parser.add_argument("--verbose", "-v", action='count', default=0,
                                help="Logging Verbosity (Default: %(default)s)")
    date_specs = gps.DateParent(group_title='Dates')

    parents = [verbose_parser, date_specs.parser]
    parser = argparse.ArgumentParser(parents=parents)

    parser.set_defaults(func=main)

    args = parser.parse_args()
    args.func(args)

