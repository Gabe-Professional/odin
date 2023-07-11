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

    TODO: improvements
    todo: summarizing data functions...
    todo: saving data functions...


    :param args:
    :type args:
    :return:
    :rtype:
    """
    # MAIN INPUTS
    database = args.database
    start_time = args.start_time
    cluster = args.cluster
    end_time = args.end_time
    subdirs = args.sub_dirs
    directories = setup_project_directory(directory=args.project_directory, subdirs=subdirs)
    direction = args.message_direction
    keywords = args.keywords
    save = args.download

    # todo: deal with data better...
    data = {}
    if database == 'postgres':
        with PG.Create(cluster) as db:

            data = db.get_messages_by_datetime(start_datetime=start_time, end_datetime=end_time,
                                               direction=direction, pretty=True)

            # todo: add saving or showing pretty data to demo...

    elif database == 'elastic':
        if not keywords:
            # logger.setLevel(level='DEBUG')
            logger.debug(f'Please provide a list of keywords to us in {database}')

        else:
            query = build_body_kw_query(keywords=keywords, start_time=start_time, end_time=end_time)
            with ES.Create(cluster) as db:
                # todo: need to troubleshoot...returning same number or results for different end dates...
                count = db.count(query=query, index_pattern='pulse')
                logger.info(f'GETTING {count} RESULTS FROM ELASTICSEARCH')
                data = db.query(query=query, index_pattern='pulse', batch_size=1000)
                # todo: should get rid of the pretty parameter and always use the function...
                df = make_pretty_df(data)
                if save:
                    logger.info(f'Saving data to {directories[list(directories)[0]]}')
                    df.to_csv(os.path.join(directories[list(directories)[0]],
                                           f'{start_time}_{end_time}_from_{database}.csv'),
                              index=False)

    return data


