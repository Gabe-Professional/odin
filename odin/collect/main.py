import logging

import pandas as pd

from .elastic_search import get_creds, make_api_call
from odin.utils.munging import clean_data, change_query_datetime
import os
from odin.utils.projects import setup_project_directory
from odin.collect.postgres import Db


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
    subdirs = args.sub_directories
    pretty = args.pretty_data
    directories = setup_project_directory(directory=args.project_directory, subdirs=subdirs)
    direction = args.message_direction

    data = {}
    if database == 'postgres':
        with Db.Create(cluster) as db:
            data = db.get_messages_by_datetime(start_datetime=start_time, end_datetime=end_time,
                                               direction=direction, pretty=pretty)

    return data


