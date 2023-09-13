import logging
import os
from odin.utils.projects import setup_project_directory
from odin.collect.postgres import Db as PG
from odin.collect.elastic_search import Db as ES
from odin.collect.elastic_search import build_body_kw_query
from odin.collect.elastic_search import make_pretty_df
logger = logging.getLogger(__name__)


def collect_main(args):
    """
    Use these arguments to query Odin data, create project directories, and summarize queried data
    """
    # MAIN INPUTS
    start_time = args.start
    cluster = args.cluster
    end_time = args.stop
    subdirs = args.sub_dirs
    keywords = args.keywords
    directories = setup_project_directory(directory=args.project_dir, subdirs=subdirs)

    data = {}
    if args.postgres:
        direction = None

        if args.download:
            logger.setLevel(level='DEBUG')
            logger.debug(f'Downloading data directly on the odin cli is not an option at this time. '
                         f'Please run your command again without the -dl option')
        else:
            if args.message_in:
                direction = 'in'

            elif args.message_out:
                direction = 'out'

            with PG.Create(cluster) as db:

                data = db.get_messages_by_datetime(start_datetime=start_time, end_datetime=end_time,
                                                   direction=direction, pretty=True)

    elif args.elastic:
        if not keywords:
            logger.setLevel(level='DEBUG')
            logger.debug(f'Please provide a list of keywords to us in {args.elastic}')

        else:
            query = build_body_kw_query(keywords=keywords, start_time=start_time, end_time=end_time)
            with ES.Create(cluster) as db:
                count = db.count(query=query, index_pattern='pulse')
                logger.info(f'GETTING {count} RESULTS FROM ELASTICSEARCH')
                data = db.query(query=query, index_pattern='pulse')
                df = make_pretty_df(data)
                if args.download:
                    logger.info(f'Saving data to {directories[list(directories)[0]]}')
                    df.to_csv(os.path.join(directories[list(directories)[0]],
                                           f'{start_time}_{end_time}_from_{"elasticsearch"}.csv'),
                              index=False)
                else:
                    logger.info(f'\n {df}')

    return data


